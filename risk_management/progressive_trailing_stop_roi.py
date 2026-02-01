import time
import threading
from order_book.cancel_orders import ConditionalOrderCanceller

SYMBOL = "BTCUSDT"

# ================= CONFIG =================

PEAK_ROI_STOP = -0.02     # 🔥 Peak থেকে -2% ROI
CHECK_INTERVAL = 2
MIN_STOP_MOVE = 8.0       # noise filter (price move)

# ================= ENGINE =================

class ProgressiveTrailingStop:
    def __init__(self, client):
        self.client = client
        self.running = False

        self.entry_price = None
        self.side = None
        self.peak_price = None
        self.last_stop_price = None
        self.cleaned_after_close = False
        self.no_position_logged = False   # ✅ NEW

    # ---------- POSITION ----------

    def get_position(self):
        positions = self.client.futures_position_information(symbol=SYMBOL)
        for p in positions:
            amt = float(p["positionAmt"])
            if amt != 0:
                return {
                    "side": "LONG" if amt > 0 else "SHORT",
                    "entry": float(p["entryPrice"]),
                    "qty": abs(amt),
                    "margin": float(p.get("initialMargin", 0))
                }
        return None

    # ---------- PEAK ROI → PRICE ----------

    def price_from_peak_roi(self, pos, roi_from_peak):
        delta = roi_from_peak * (pos["margin"] / pos["qty"])
        return (
            self.peak_price + delta
            if pos["side"] == "LONG"
            else self.peak_price - delta
        )

    # ---------- STOP CONTROL ----------

    def place_stop(self, pos, stop):
        stop = round(stop, 2)

        if self.last_stop_price == stop:
            return

        ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()

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
        print(f"🛑 PEAK ROI SL SET → {stop}")

    # ---------- MAIN LOOP ----------

    def run(self):
        self.running = True
        print("🔥 Smart Trailing Engine STARTED (PURE PEAK-ROI + FULL SIGNALS)")

        while self.running:
            try:
                price = float(
                    self.client.futures_mark_price(symbol=SYMBOL)["markPrice"]
                )

                pos = self.get_position()

                # ===== NO POSITION =====
                if not pos:
                    if not self.cleaned_after_close:
                        ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()
                        self.cleaned_after_close = True

                    if not self.no_position_logged:
                        print("⏸ No open position detected. Waiting...")
                        self.no_position_logged = True

                    self.entry_price = None
                    self.side = None
                    self.peak_price = None
                    self.last_stop_price = None
                    time.sleep(2)
                    continue

                # ===== NEW POSITION =====
                if self.entry_price is None:
                    self.cleaned_after_close = False
                    self.no_position_logged = False   # ✅ reset
                    self.entry_price = pos["entry"]
                    self.side = pos["side"]
                    self.peak_price = price
                    self.last_stop_price = None
                    print(f"📌 {self.side} ENTRY @ {self.entry_price}")

                # ===== PEAK TRACK =====
                if pos["side"] == "LONG":
                    self.peak_price = max(self.peak_price, price)
                else:
                    self.peak_price = min(self.peak_price, price)

                # ===== PEAK ROI STOP =====
                stop = self.price_from_peak_roi(pos, PEAK_ROI_STOP)

                if (
                    self.last_stop_price is None
                    or abs(stop - self.last_stop_price) >= MIN_STOP_MOVE
                ):
                    self.place_stop(pos, stop)

                # ===== INFO PRINT =====
                pnl = (
                    pos["qty"] * (price - self.entry_price)
                    if self.side == "LONG"
                    else pos["qty"] * (self.entry_price - price)
                )
                roi = pnl / pos["margin"] if pos["margin"] > 0 else 0.0

                print(
                    f"{self.side} | "
                    f"Entry {self.entry_price:.2f} | "
                    f"Price {price:.2f} | "
                    f"Peak {self.peak_price:.2f} | "
                    f"PNL {pnl:.2f} | "
                    f"ROI {roi * 100:.2f}%"
                )

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("❌ Engine error:", e)
                time.sleep(3)


# ================= STAND-ALONE =================

if __name__ == "__main__":
    from api_callling.api_calling import APICall

    ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()

    api = APICall()
    client = api.client

    engine = ProgressiveTrailingStop(client)
    threading.Thread(target=engine.run, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Engine stopped")
