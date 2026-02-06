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
from all_variable import Variable

# ================= CONFIG =================

SYMBOL = Variable.SYMBOL
RISK = Variable.RISK
LEVERAGE = int(Variable.LAVARAGE)
ENTRY_MODE = Variable.ENTRY_MODE  # LONG, SHORT, BOTH

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
    safe_entry_long = SafeEntry(client=client)
    safe_entry_short = SafeEntry(client=client)

    # ================= ENTRY FLOW =================

    chosen_side = None

    if ENTRY_MODE == "LONG":
        print("🔐 Waiting for SAFE LONG entry...")
        safe_entry_long.long()
        while safe_entry_long.active:
            time.sleep(0.2)
        if safe_entry_long.confirmed:
            chosen_side = "LONG"
        elif safe_entry_long.timed_out:
            print("⏱ SAFE ENTRY TIMED OUT — NO TRADE")

    elif ENTRY_MODE == "SHORT":
        print("🔐 Waiting for SAFE SHORT entry...")
        safe_entry_short.short()
        while safe_entry_short.active:
            time.sleep(0.2)
        if safe_entry_short.confirmed:
            chosen_side = "SHORT"
        elif safe_entry_short.timed_out:
            print("⏱ SAFE ENTRY TIMED OUT — NO TRADE")

    else:
        print("🔐 Waiting for SAFE LONG/SHORT entry...")
        safe_entry_long.long()
        safe_entry_short.short()

        while True:
            if safe_entry_long.confirmed:
                chosen_side = "LONG"
                safe_entry_short.active = False
                break
            if safe_entry_short.confirmed:
                chosen_side = "SHORT"
                safe_entry_long.active = False
                break
            if safe_entry_long.timed_out and safe_entry_short.timed_out:
                print("⏱ SAFE ENTRY TIMED OUT — NO TRADE")
                break
            time.sleep(0.2)

    if chosen_side and not TRADE_ACTIVE:
        print(f"🚀 SAFE ENTRY CONFIRMED → EXECUTING {chosen_side}")
        if chosen_side == "LONG":
            trader.long(
                symbol=SYMBOL,
                risk=RISK,
                lev=LEVERAGE
            )
        else:
            trader.short(
                symbol=SYMBOL,
                risk=RISK,
                lev=LEVERAGE
            )

        time.sleep(0.5)  # allow position to appear

        trailing_engine.start()
        TRADE_ACTIVE = True

        print("🔥 TRADE ACTIVE — Trailing engine running")

    # ================= KEEP ALIVE =================

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 SAFE MAIN STOPPED")

# ================= RUN =================

if __name__ == "__main__":
    main()
