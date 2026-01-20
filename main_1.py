import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import sqlite3
import asyncio
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
# GLOBAL STATE
# ======================================================

TRADE_ACTIVE = False


# ======================================================
# SAFE ENTRY INSTANCE
# ======================================================

safe_entry = SafeEntry(
    symbol="BTCUSDT",
    safe_distance_pct=0.0015,
    confirm_ticks=2,
    max_wait=120,
)


# ======================================================
# API & ENGINES
# ======================================================

api = APICall()
client = api.client

long_sl = LongStopLoss(client)
short_sl = ShortStopLoss(client)

trader = MarketOrder(client, long_sl, short_sl)
trailing_engine = ProgressiveTrailingStop(client)

database = os.path.abspath(Variable.DATABASE)


# ======================================================
# SAFE ENTRY WAIT (SYNC)
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
# SAFE INDICATOR FLATTENER (NO pandas crash)
# ======================================================

def flatten_indicators(row):
    result = []
    for item in row:
        if isinstance(item, list):
            result.extend(item)
    return result


# ======================================================
# MAIN LOGIC
# ======================================================

def main():
    global TRADE_ACTIVE
    import pandas as pd

    if TRADE_ACTIVE:
        print("⏸ Trade already active — skipping")
        return

    target_symbol = "BTCUSDT"
    timelines = [5, 15, 30, 60, 240, 1440, 10080]
    lookback = 1440 * 30

    missing = MissingDataCollection(database=database)
    missing.collect_missing_data_single_symbols(target_symbol)

    frames = []

    for timeline in timelines:
        conn = sqlite3.connect(database)
        db = GetDbDataframe(conn)

        data = db.get_minute_data(target_symbol, timeline, lookback)
        df = db.get_all_indicators(target_symbol, timeline, lookback)

        df.index = data.index
        df = df.add_prefix(f"{timeline}_")

        data[f"Sum_{timeline}m"] = df.sum(axis=1)
        data[f"Indicators_{timeline}m"] = df.apply(
            lambda r: [(c, r[c]) for c in df.columns if r[c] != 0],
            axis=1
        )

        frames.append(
            data.tail(1)[[f"Sum_{timeline}m", f"Indicators_{timeline}m"]]
        )

    final = pd.concat(frames, axis=1)

    sum_cols = [c for c in final.columns if c.startswith("Sum_")]
    ind_cols = [c for c in final.columns if c.startswith("Indicators_")]

    final[sum_cols] = final[sum_cols].fillna(0)

    final["Total_Sum"] = final[sum_cols].sum(axis=1)
    final["Total_Indicators"] = final[ind_cols].apply(flatten_indicators, axis=1)

    signal = final["Total_Sum"].iloc[0]
    print(f"📊 Signal Sum → {signal}")

    # =========================
    # LONG
    # =========================

    if signal >= 1200 and not safe_entry.active:
        print("🟢 LONG signal")

        safe_entry.long()
        confirmed = wait_safe_entry(safe_entry)

        if confirmed:
            trader.long("BTCUSDT", 1, 4)
            trailing_engine.start()
            playsound("sounds/Bullish.wav")
            TRADE_ACTIVE = True
            print("✅ LONG EXECUTED")
        else:
            print("❌ LONG rejected by Safe Entry")

    # =========================
    # SHORT
    # =========================

    elif signal <= -1200 and not safe_entry.active:
        print("🔴 SHORT signal")

        safe_entry.short()
        confirmed = wait_safe_entry(safe_entry)

        if confirmed:
            trader.short("BTCUSDT", 1, 4)
            trailing_engine.start()
            playsound("sounds/Bearish.wav")
            TRADE_ACTIVE = True
            print("✅ SHORT EXECUTED")
        else:
            print("❌ SHORT rejected by Safe Entry")


# ======================================================
# LOOP
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
