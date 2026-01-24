import time
import threading
from order_book.cancel_orders import ConditionalOrderCanceller

SYMBOL = "BTCUSDT"

# ================= CONFIG =================

ROI_TIERS = [
    (0.10, 0.005),
    (0.05, 0.01),    (0.00, 0.02),
]

BREAKEVEN_ROI = 0.02
CHECK_INTERVAL = 2
MIN_STOP_MOVE = 5.0          # minimum price change to update SL
CANCEL_VERIFY_RETRY = 10     # max retries to verify cancel
CANCEL_VERIFY_DELAY = 0.2    # delay between retries


# ================= ENGINE =================

class SmartTrailingEngine:
    def __init__(self, client):
        self.client = client
        self.running = False

        self.entry_price = None
        self.side = None
        self.peak_price = None
        self.last_stop_price = None
        self.breakeven_locked = False
        self.cleaned_after_close = False

    # ---------- utilities ----------

    def trailing_percent(self, roi):
        for level, pct in ROI_TIERS:
            if roi >= level:
                return pct
        return 0.02

    def get_position(self):
        positions = self.client.futures_position_information(symbol=SYMBOL)
        for p in positions:
            amt = float(p["positionAmt"])
            if amt != 0:
                margin = float(p.get("initialMargin", 0))
                return {
                    "side": "LONG" if amt > 0 else "SHORT",
                    "entry": float(p["entryPrice"]),
                    "qty": abs(amt),
                    "margin": margin
                }
        return None

    def calc_pnl_and_roi(self, pos, price):
        pnl = (
            pos["qty"] * (price - pos["entry"])
            if pos["side"] == "LONG"
            else pos["qty"] * (pos["entry"] - price)
        )
        base = pos["margin"] if pos["margin"] > 0 else pos["entry"] * pos["qty"]
        roi = pnl / base if base > 0 else 0.0
        return pnl, roi


    # ---------- STOP CONTROL (HARD & SAFE) ----------

    def cancel_all_stop_orders(self):
        """
        Atomic cancel + verification.
        Ensures ZERO conditional orders before placing new SL.
        """
        self.client.futures_cancel_all_open_orders(symbol=SYMBOL)

        for _ in range(CANCEL_VERIFY_RETRY):
            orders = self.client.futures_get_open_orders(symbol=SYMBOL)
            stops = [
                o for o in orders
                if o["type"] in ("STOP_MARKET", "TAKE_PROFIT_MARKET")
            ]
            if not stops:
                return
            time.sleep(CANCEL_VERIFY_DELAY)

        print("⚠️ WARNING: Some stop orders may not have been cleared")


    def place_trailing_stop(self, pos, stop):
        # Prevent duplicate SL at same price (especially entry)
        if self.last_stop_price == stop:
            return

        # ✅ HARD GUARANTEE: previous stop is gone
        ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()

        # 🔥 HARD RESET
        # self.cancel_all_stop_orders()

        self.client.futures_create_order(
            symbol=SYMBOL,
            side="SELL" if pos["side"] == "LONG" else "BUY",
            type="STOP_MARKET",
            stopPrice=stop,
            quantity=round(pos["qty"], 3),
            reduceOnly=True,
            workingType="MARK_PRICE"
        )

        self.last_stop_price = stop
        print(f"🛑 SL SET → {stop}")


    # ---------- MAIN LOOP ----------

    def run(self):
        self.running = True
        print("🔥 Smart Trailing Engine STARTED")

        while self.running:
            try:
                price = float(
                    self.client.futures_mark_price(symbol=SYMBOL)["markPrice"]
                )

                pos = self.get_position()

                # ===== NO POSITION =====
                if not pos:
                    # 🧹 Position closed → hard cleanup ONCE
                    if not self.cleaned_after_close:
                        ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()
                        self.cleaned_after_close = True
                        print("🧹 Position closed → all stops cleared")

                    self.entry_price = None
                    self.side = None
                    self.peak_price = None
                    self.last_stop_price = None
                    self.breakeven_locked = False
                    time.sleep(3)
                    continue

                # ===== NEW POSITION =====
                if self.entry_price is None:
                    self.cleaned_after_close = False
                    self.entry_price = pos["entry"]
                    self.side = pos["side"]
                    self.peak_price = pos["entry"]
                    self.last_stop_price = None
                    self.breakeven_locked = False
                    print(f"📌 {self.side} ENTRY @ {self.entry_price}")

                # ===== PEAK TRACKING =====
                if pos["side"] == "LONG":
                    self.peak_price = max(self.peak_price, price)
                else:
                    self.peak_price = min(self.peak_price, price)

                pnl, roi = self.calc_pnl_and_roi(pos, price)

                # ===== TRAILING LOGIC =====
                trail_pct = self.trailing_percent(roi)
                stop = (
                    self.peak_price * (1 - trail_pct)
                    if pos["side"] == "LONG"
                    else self.peak_price * (1 + trail_pct)
                )

                # ===== BREAKEVEN (LOCK ONCE) =====
                if roi >= BREAKEVEN_ROI and not self.breakeven_locked:
                    stop = pos["entry"]
                    self.breakeven_locked = True
                elif self.breakeven_locked:
                    stop = (
                        max(stop, pos["entry"])
                        if pos["side"] == "LONG"
                        else min(stop, pos["entry"])
                    )

                stop = round(stop, 2)

                # ===== NOISE FILTER =====
                if (
                    self.last_stop_price is None
                    or abs(stop - self.last_stop_price) >= MIN_STOP_MOVE
                ):
                    self.place_trailing_stop(pos, stop)

                print(
                    f"{pos['side']} | "
                    f"Entry {pos['entry']:.2f} | "
                    f"Price {price:.2f} | "
                    f"Peak {self.peak_price:.2f} | "
                    f"PNL {pnl:.2f} | "
                    f"ROI {roi * 100:.2f}%"
                )

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("❌ Engine error:", e)
                time.sleep(3)


# ================= RUN =================

# ======================================================
# COMPATIBILITY WRAPPER (DO NOT REMOVE)
# ======================================================

class ProgressiveTrailingStop(SmartTrailingEngine):
    def start(self):
        import threading
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()


if __name__ == "__main__":
    from api_callling.api_calling import APICall

    # 🔥 HARD RESET (stand-alone safe)
    canceller = ConditionalOrderCanceller(symbol="BTCUSDT")
    canceller.cancel_all()

    api = APICall()
    client = api.client

    engine = SmartTrailingEngine(client)
    threading.Thread(target=engine.run, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Engine stopped")
