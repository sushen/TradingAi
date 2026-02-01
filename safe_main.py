# safe_main.py

import time
import threading

# ================= IMPORTS =================

from api_callling.api_calling import APICall
from order_book.market_order import MarketOrder
from risk_management.safe_entry import SafeEntry
from risk_management.progressive_trailing_stop import ProgressiveTrailingStop
from order_book.long_stop_loss import LongStopLoss
from order_book.short_stop_loss import ShortStopLoss
from order_book.cancel_orders import ConditionalOrderCanceller

# ================= CONFIG =================

SYMBOL = "BTCUSDT"
RISK = 1
LEVERAGE = 4

TRADE_ACTIVE = False

# ================= MAIN =================

def main():
    global TRADE_ACTIVE

    print("🛡 SAFE MAIN STARTED")

    # ---------- HARD RESET ----------
    ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()
    print("🧹 All conditional orders cleared")

    # ---------- API ----------
    api = APICall()
    client = api.client

    # ---------- STOP ENGINES ----------
    long_sl = LongStopLoss(client)
    short_sl = ShortStopLoss(client)

    # ---------- MARKET ORDER ----------
    trader = MarketOrder(
        client=client,
        long_sl=long_sl,
        short_sl=short_sl
    )

    # ---------- TRAILING ENGINE ----------
    trailing_engine = ProgressiveTrailingStop(client)

    # ---------- SAFE ENTRY ----------
    safe_entry = SafeEntry()

    # ================= ENTRY FLOW =================

    print("🔐 Waiting for SAFE LONG entry...")
    safe_entry.long()

    while safe_entry.active:
        time.sleep(0.2)

    if safe_entry.confirmed and not TRADE_ACTIVE:
        print("🚀 SAFE ENTRY CONFIRMED → EXECUTING LONG")

        trader.long(
            symbol=SYMBOL,
            risk=RISK,
            lev=LEVERAGE
        )

        time.sleep(0.5)  # allow position to appear

        trailing_engine.start()
        TRADE_ACTIVE = True

        print("🔥 TRADE ACTIVE — Trailing engine running")

    elif safe_entry.timed_out:
        print("⏱ SAFE ENTRY TIMED OUT — NO TRADE")

    # ================= KEEP ALIVE =================

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 SAFE MAIN STOPPED")

# ================= RUN =================

if __name__ == "__main__":
    main()
