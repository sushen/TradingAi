import time
import threading

SYMBOL = "BTCUSDT"

# ================= CONFIG =================

ROI_TIERS = [
    (0.10, 0.005),
    (0.05, 0.01),
    (0.00, 0.02),
]

BREAKEVEN_ROI = 0.02
CHECK_INTERVAL = 2
CANCEL_WAIT = 0.5
MIN_STOP_MOVE = 5.0   # 🔑 minimum price change to update SL


# ================= ENGINE =================

class SmartTrailingEngine:
    def __init__(self, client):
        self.client = client
        self.running = False

        self.entry_price = None
        self.side = None
        self.peak_price = None

        self.last_stop_price = None
        self.cleaned_existing_stops = False


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


    # ---------- STOP CONTROL ----------

    def cancel_all_stops_once(self):
        orders = self.client.futures_get_open_orders(symbol=SYMBOL)
        for o in orders:
            if o.get("stopPrice") is not None:
                self.client.futures_cancel_order(
                    symbol=SYMBOL,
                    orderId=o["orderId"]
                )
        time.sleep(CANCEL_WAIT)

    def cancel_own_trailing_stop(self):
        orders = self.client.futures_get_open_orders(symbol=SYMBOL)
        for o in orders:
            if o.get("reduceOnly") and o["type"] == "STOP_MARKET":
                self.client.futures_cancel_order(
                    symbol=SYMBOL,
                    orderId=o["orderId"]
                )
        time.sleep(CANCEL_WAIT)

    def place_trailing_stop(self, pos, stop):
        self.cancel_own_trailing_stop()

        self.client.futures_create_order(
            symbol=SYMBOL,
            side="SELL" if pos["side"] == "LONG" else "BUY",
            type="STOP_MARKET",
            stopPrice=stop,
            quantity=round(pos["qty"], 3),
            reduceOnly=True,
            workingType="MARK_PRICE"
        )

        print(f"🛑 TRAILING SL → {stop}")


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
                if not pos:
                    self.entry_price = None
                    self.peak_price = None
                    self.last_stop_price = None
                    self.cleaned_existing_stops = False
                    time.sleep(3)
                    continue

                # first detection
                if self.entry_price is None:
                    self.entry_price = pos["entry"]
                    self.side = pos["side"]
                    self.peak_price = pos["entry"]
                    print(f"📌 {self.side} ENTRY @ {self.entry_price}")

                # clean legacy stops ONCE
                if not self.cleaned_existing_stops:
                    self.cancel_all_stops_once()
                    self.cleaned_existing_stops = True
                    print("🧹 Old SL/TP cleaned")

                # peak tracking
                if pos["side"] == "LONG":
                    self.peak_price = max(self.peak_price, price)
                else:
                    self.peak_price = min(self.peak_price, price)

                pnl, roi = self.calc_pnl_and_roi(pos, price)

                trail_pct = self.trailing_percent(roi)
                stop = (
                    self.peak_price * (1 - trail_pct)
                    if pos["side"] == "LONG"
                    else self.peak_price * (1 + trail_pct)
                )

                if roi >= BREAKEVEN_ROI:
                    stop = (
                        max(stop, pos["entry"])
                        if pos["side"] == "LONG"
                        else min(stop, pos["entry"])
                    )

                stop = round(stop, 2)

                # minimum movement filter
                if (
                    self.last_stop_price is None
                    or abs(stop - self.last_stop_price) >= MIN_STOP_MOVE
                ):
                    self.place_trailing_stop(pos, stop)
                    self.last_stop_price = stop

                print(
                    f"{pos['side']} | "
                    f"Entry {pos['entry']:.2f} | "
                    f"Price {price:.2f} | "
                    f"Peak {self.peak_price:.2f} | "
                    f"PNL {pnl:.2f} USDT | "
                    f"ROI {roi * 100:.2f}%"
                )

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("❌ Engine error:", e)
                time.sleep(3)


# ================= RUN =================

if __name__ == "__main__":
    from api_callling.api_calling import APICall

    api = APICall()
    client = api.client

    engine = SmartTrailingEngine(client)
    threading.Thread(target=engine.run).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Engine stopped")
