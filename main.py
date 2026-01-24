import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import sqlite3
import asyncio
import numpy as np
from playsound import playsound

from dataframe.db_dataframe import GetDbDataframe
from database.missing_data_single_symbol import MissingDataCollection
from api_callling.api_calling import APICall
from order_book.market_order import MarketOrder
from order_book.long_stop_loss import LongStopLoss
from order_book.short_stop_loss import ShortStopLoss
from risk_management.progressive_trailing_stop import ProgressiveTrailingStop
from risk_management.safe_entry import SafeEntry
from all_variable import Variable


# ======================================================
# GLOBAL STATE (execution only, NOT indicators)
# ======================================================
TRADE_ACTIVE = False


# ======================================================
# SAFE ENTRY (secondary system)
# ======================================================
safe_entry = SafeEntry(
    symbol="BTCUSDT",
    safe_distance_pct=0.001,
    confirm_ticks=1,
    max_wait=240,
)


# ======================================================
# API & ENGINES (execution only)
# ======================================================
api = APICall()
client = api.client

long_sl = LongStopLoss(client)
short_sl = ShortStopLoss(client)

trader = MarketOrder(client, long_sl, short_sl)
trailing_engine = ProgressiveTrailingStop(client)

database = os.path.abspath(Variable.DATABASE)


# ======================================================
# SAFE ENTRY WAIT (NO impact on indicators)
# ======================================================
def wait_safe_entry(entry: SafeEntry) -> bool:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_wait(entry))
    finally:
        loop.close()

async def _wait(entry: SafeEntry):
    while entry.active and not entry.confirmed and not entry.timed_out:
        await asyncio.sleep(0.1)
    return entry.confirmed


# ======================================================
# SAFE FLATTEN (does NOT change indicator values)
# ======================================================
def flatten_indicators(row):
    result = []
    for item in row:
        if isinstance(item, list):
            result.extend(item)
    return result


# ======================================================
# MAIN (INDICATORS = main_2.py EXACT)
# ======================================================
def main():
    global TRADE_ACTIVE
    import pandas as pd

    target_symbol = "BTCUSDT"
    timelines = [5, 15, 30, 60, 240, 1440, 10080]
    lookback = 1440 * 30

    # --- EXACT same DB sync as main_2 ---
    MissingDataCollection(database=database)\
        .collect_missing_data_single_symbols(target_symbol)

    # we will NOT use pandas to compute final signal
    final_signal = 0
    indicator_frames = []

    for timeline in timelines:
        conn = sqlite3.connect(database)
        db = GetDbDataframe(conn)

        data = db.get_minute_data(target_symbol, timeline, lookback)
        df = db.get_all_indicators(target_symbol, timeline, lookback)

        # --- EXACT alignment ---
        df.index = data.index
        df = df.add_prefix(f"{timeline}_")

        # ==================================================
        # 🔥 EXACT indicator logic from main_2.py (UNTOUCHED)
        # ==================================================
        data[f"Sum_{timeline}m"] = df.sum(axis=1)

        total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
        total_sum_values = total_sum_values.add(
            data[f"Sum_{timeline}m"], fill_value=0
        )
        total_sum_values = total_sum_values.fillna(0).astype(np.int16)

        data[f"Sum_{timeline}m"] = total_sum_values

        data[f"Indicators_{timeline}m"] = df.apply(
            lambda r: [(c, r[c]) for c in df.columns if r[c] != 0],
            axis=1
        )

        # ==================================================
        # 🔑 EXACT final signal behavior (NO pandas sum)
        # ==================================================
        last_sum = data[f"Sum_{timeline}m"].iloc[-1]
        final_signal += int(last_sum)

        indicator_frames.append(
            data.tail(1)[[f"Indicators_{timeline}m"]]
        )

    # combine indicators only for visibility (NOT math)
    indicators_df = pd.concat(indicator_frames, axis=1)
    total_indicators = indicators_df.apply(flatten_indicators, axis=1).iloc[0]

    print(f"📊 FINAL Signal Sum → {final_signal}")

    # ==================================================
    # EXECUTION (secondary, optional)
    # ==================================================
    if final_signal >= 1600 and not safe_entry.active and not TRADE_ACTIVE:
        print("🟢 LONG signal")
        safe_entry.long()
        if wait_safe_entry(safe_entry):
            trader.long("BTCUSDT", 1, 4)
            trailing_engine.start()
            playsound("sounds/Bullish.wav")
            TRADE_ACTIVE = True

    elif final_signal <= -1600 and not safe_entry.active and not TRADE_ACTIVE:
        print("🔴 SHORT signal")
        safe_entry.short()
        if wait_safe_entry(safe_entry):
            trader.short("BTCUSDT", 1, 4)
            trailing_engine.start()
            playsound("sounds/Bearish.wav")
            TRADE_ACTIVE = True


# ======================================================
# LOOP (same rhythm as main_2)
# ======================================================
START = time.time()

while True:
    loop_start = time.time()
    main()

    elapsed = time.time() - loop_start
    sleep_time = max(1, 60 - elapsed)

    print(f"⏱ Loop: {elapsed:.2f}s | Sleep: {sleep_time:.2f}s")

    time.sleep(sleep_time)

    runtime = (time.time() - START) / 60
    print(f"🕒 Runtime: {runtime:.1f} minutes\n")
