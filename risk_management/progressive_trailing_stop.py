import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import threading

SYMBOL = "BTCUSDT"

ROI_TIERS = [
    (0.10, 0.005),
    (0.05, 0.01),
    (0.00, 0.02),
]

MIN_PNL_IMPROVEMENT = 0.5  # USDT


class ProgressiveTrailingStop:
    def __init__(self, client):
        self.client = client
        self.running = False
        self.thread = None

        self.position_side = None
        self.price_peak = None
        self.locked_pnl = 0.0

    # ---------- helpers ----------
    def trailing_percent(self, roi):
        for level, percent in ROI_TIERS:
            if roi >= level:
                return percent
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
                    "amt": abs(amt),
                    "margin": margin,
                    "leverage": float(p.get("leverage", 1)),
                }
        return None

    def calc_pnl_and_roi(self, pos, price):
        pnl = (
            pos["amt"] * (price - pos["entry"])
            if pos["side"] == "LONG"
            else pos["amt"] * (pos["entry"] - price)
        )
        roi = pnl / pos["margin"] if pos["margin"] > 1e-8 else 0.0
        return pnl, roi

    # ---------- stop logic ----------
    def update_trailing_stop(self, pos, peak_price, trail_pct):
        side = pos["side"]
        stop_price = (
            round(peak_price * (1 - trail_pct), 2)
            if side == "LONG"
            else round(peak_price * (1 + trail_pct), 2)
        )
        close_side = "SELL" if side == "LONG" else "BUY"

        orders = self.client.futures_get_open_orders(symbol=SYMBOL)
        for o in orders:
            if o["type"] in (
                "STOP_MARKET",
                "TAKE_PROFIT_MARKET",
                "STOP",
                "TAKE_PROFIT",
            ):
                self.client.futures_cancel_order(
                    symbol=SYMBOL,
                    orderId=o["orderId"]
                )

        self.client.futures_create_order(
            symbol=SYMBOL,
            side=close_side,
            type="STOP_MARKET",
            stopPrice=stop_price,
            closePosition=True,
        )

        print(f"🛑 STOP → {stop_price} | Trail {trail_pct*100:.2f}%")

    # ---------- engine ----------
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        print("🔥 Progressive Trailing Engine started")

    def stop(self):
        self.running = False
        self.position_side = None
        self.price_peak = None
        self.locked_pnl = 0.0
        print("🛑 Progressive Trailing Engine stopped")

    def run(self):
        while self.running:
            try:
                price = float(
                    self.client.futures_mark_price(symbol=SYMBOL)["markPrice"]
                )
                pos = self.get_position()

                if not pos:
                    self.stop()
                    time.sleep(3)
                    continue

                if self.position_side is None:
                    self.position_side = pos["side"]
                    self.price_peak = pos["entry"]
                    self.locked_pnl = 0.0
                    print(f"📌 {self.position_side} ENTRY {pos['entry']}")

                if pos["side"] == "LONG":
                    self.price_peak = max(self.price_peak, price)
                else:
                    self.price_peak = min(self.price_peak, price)

                live_pnl, live_roi = self.calc_pnl_and_roi(pos, price)
                peak_pnl, peak_roi = self.calc_pnl_and_roi(pos, self.price_peak)

                if peak_pnl > self.locked_pnl + MIN_PNL_IMPROVEMENT:
                    self.locked_pnl = peak_pnl
                    trail = self.trailing_percent(peak_roi)
                    self.update_trailing_stop(pos, self.price_peak, trail)

                print(
                    f"{pos['side']} | Entry {pos['entry']} | "
                    f"Mark {price} | Peak {self.price_peak} | "
                    f"PNL {live_pnl:.2f} | ROI {live_roi*100:.2f}%"
                )

                time.sleep(2)

            except Exception as e:
                print("Trailing engine error:", e)
                time.sleep(5)

if __name__ == "__main__":
    """
    DEBUG / STANDALONE TEST MODE ONLY
    --------------------------------
    This block is NOT used by main.py.
    It allows testing the trailing engine independently.
    """

    from api_callling.api_calling import APICall

    api = APICall()
    client = api.client

    engine = ProgressiveTrailingStop(client)
    engine.start()

    # keep process alive for observation
    while True:
        time.sleep(60)
