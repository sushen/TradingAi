import socket
socket.setdefaulttimeout(30)

import os
import ctypes
import sys
import time
import sqlite3
import asyncio
import numpy as np
from playsound import playsound
import platform

from dataframe.db_dataframe import GetDbDataframe
from database.missing_data_single_symbol import MissingDataCollection
from api_callling.api_calling import APICall
from order_book.market_order import MarketOrder
from order_book.long_stop_loss import LongStopLoss
from order_book.short_stop_loss import ShortStopLoss
from risk_management.progressive_trailing_stop import ProgressiveTrailingStop
from risk_management.safe_entry import SafeEntry
from all_variable import Variable
from sounds.sound_engine import SoundEngine

sound = SoundEngine()
LAST_SPOKEN_SIGNAL = None

class TradingBot:
    def __init__(self, on_signal=None, on_price=None):
        # ===============================
        # PREVENT WINDOWS SLEEP
        # ===============================
        if os.name == "nt":
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            )

        # ===============================
        # STATE
        # ===============================
        self.TRADE_ACTIVE = False
        self.LAST_SPOKEN_PRICE = None
        self.LAST_SPOKEN_SIGNAL = None

        # ===============================
        # ENGINES
        # ===============================
        self.sound = SoundEngine()
        self.safe_entry = SafeEntry()

        self.api = APICall()
        self.client = self.api.client

        self.long_sl = LongStopLoss(self.client)
        self.short_sl = ShortStopLoss(self.client)

        self.trader = MarketOrder(self.client, self.long_sl, self.short_sl)
        self.trailing_engine = ProgressiveTrailingStop(self.client)

        self.database = os.path.abspath(Variable.DATABASE)

        # ===============================
        # CONFIG
        # ===============================
        self.target_symbol = "BTCUSDT"
        self.timelines = [5, 15, 30, 60, 240, 1440, 10080]
        self.lookback = 1440 * 30

        self.on_signal = on_signal
        self.on_price = on_price

    # ======================================================
    # SAFE ENTRY WAIT
    # ======================================================
    def wait_safe_entry(self) -> bool:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._wait())
        finally:
            loop.close()

    async def _wait(self):
        while self.safe_entry.active and not self.safe_entry.confirmed and not self.safe_entry.timed_out:
            await asyncio.sleep(0.1)
        return self.safe_entry.confirmed

    # ======================================================
    # FLATTEN INDICATORS
    # ======================================================
    @staticmethod
    def flatten_indicators(row):
        result = []
        for item in row:
            if isinstance(item, list):
                result.extend(item)
        return result

    # ======================================================
    # ONE LOOP STEP (formerly main())
    # ======================================================
    def _run_cycle(self):
        import pandas as pd

        MissingDataCollection(database=self.database)\
            .collect_missing_data_single_symbols(self.target_symbol)

        final_signal = 0
        indicator_frames = []

        last_close = None

        for timeline in self.timelines:
            conn = sqlite3.connect(self.database)
            db = GetDbDataframe(conn)

            data = db.get_minute_data(self.target_symbol, timeline, self.lookback)
            df = db.get_all_indicators(self.target_symbol, timeline, self.lookback)

            if last_close is None and not data.empty:
                last_close = float(data["Close"].iloc[-1])

            df.index = data.index
            df = df.add_prefix(f"{timeline}_")

            data[f"Sum_{timeline}m"] = df.sum(axis=1)
            last_sum = data[f"Sum_{timeline}m"].iloc[-1]
            final_signal += int(last_sum)

            indicator_frames.append(
                data.tail(1)[[f"Sum_{timeline}m"]]
            )

            conn.close()

        global LAST_SPOKEN_SIGNAL

        print(f"📊 FINAL Signal Sum → {final_signal}")

        if last_close is not None:
            gue_price = int(round(last_close * 100_000_000))
            print(f"₿ BTCUSDT Price → {last_close:.2f} | {gue_price:,} GUE")

        if self.on_signal:
            self.on_signal(final_signal)

        if self.on_price and last_close is not None:
            self.on_price(last_close)

        if LAST_SPOKEN_SIGNAL != final_signal:
            sound.voice_alert(f"Signal {final_signal}")
            LAST_SPOKEN_SIGNAL = final_signal

        # ===============================
        # EXECUTION
        # ===============================
        if final_signal >= 1600 and not self.safe_entry.active and not self.TRADE_ACTIVE:
            print("🟢 LONG signal")
            self.safe_entry.long()
            if self.wait_safe_entry():
                self.trader.long("BTCUSDT", 1, 6)
                self.trailing_engine.start()
                playsound("sounds/Bullish.wav")
                self.TRADE_ACTIVE = True

        elif final_signal <= -1600 and not self.safe_entry.active and not self.TRADE_ACTIVE:
            print("🔴 SHORT signal")
            self.safe_entry.short()
            if self.wait_safe_entry():
                self.trader.short("BTCUSDT", 1, 4)
                self.trailing_engine.start()
                playsound("sounds/Bearish.wav")
                self.TRADE_ACTIVE = True

    # ======================================================
    # 🔥 PUBLIC METHOD (THIS IS WHAT SUBSCRIPTION CALLS)
    # ======================================================
    def run_trading_bot(self):
        print("🚀 Trading Bot Started")
        start = time.monotonic()

        while True:
            loop_start = time.monotonic()
            self._run_cycle()

            elapsed = time.monotonic() - loop_start
            sleep_time = max(1, 60 - elapsed)

            print(f"🕒 Loop: {elapsed:.2f}s | Sleep: {sleep_time:.2f}s")
            time.sleep(sleep_time)

            runtime = (time.monotonic() - start) / 60
            print(f"🕒 Runtime: {runtime:.1f} minutes\n")
