import os
import sys
import time
import threading
import winsound
from binance.exceptions import BinanceAPIException

# ---------------- PATH FIX ----------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ---------------- ALERT SYSTEM ----------------
def alert_ip_change_loop(stop_flag):
    """
    Continuously alerts until stop_flag["stop"] becomes True
    """
    while not stop_flag["stop"]:
        winsound.Beep(1000, 500)
        time.sleep(1.5)

# ---------------- MARKET ORDER ENGINE ----------------
class MarketOrder:
    def __init__(self, client, long_sl, short_sl):
        self.client = client
        self.long_sl = long_sl
        self.short_sl = short_sl

    def get_open_position(self, symbol):
        pos = self.client.futures_position_information(symbol=symbol)
        for p in pos:
            if float(p["positionAmt"]) != 0:
                return p
        return None

    def get_balance(self):
        while True:
            try:
                for b in self.client.futures_account_balance():
                    if b["asset"] == "USDT":
                        return float(b["balance"])

            except BinanceAPIException as e:
                if e.code == -2015:
                    print("\n🔐 IP CHANGED / API BLOCKED")
                    print("👉 Please update IP whitelist in Binance")
                    print("🔊 Alert will continue until you press ENTER")

                    stop_flag = {"stop": False}

                    alert_thread = threading.Thread(
                        target=alert_ip_change_loop,
                        args=(stop_flag,),
                        daemon=True
                    )
                    alert_thread.start()

                    input("⏸️ IP ঠিক করে ENTER চাপুন...")

                    stop_flag["stop"] = True
                    time.sleep(0.5)

                    print("🔁 Rechecking balance...\n")
                    time.sleep(1)
                    continue
                else:
                    raise e

    def get_price(self, symbol):
        return float(self.client.futures_mark_price(symbol=symbol)["markPrice"])

    def get_lot(self, symbol):
        info = self.client.futures_exchange_info()
        for s in info["symbols"]:
            if s["symbol"] == symbol:
                for f in s["filters"]:
                    if f["filterType"] == "LOT_SIZE":
                        return float(f["minQty"]), float(f["stepSize"])

    def calc_qty(self, symbol, risk, lev):
        bal = self.get_balance()
        price = self.get_price(symbol)
        min_qty, step = self.get_lot(symbol)

        margin = bal * risk
        notional = max(margin * lev, 100)
        qty = notional / price
        qty = max(qty, min_qty)

        return float(f"{(qty // step) * step:.8f}")

    def long(self, symbol, risk=1, lev=3):
        qty = self.calc_qty(symbol, risk, lev)
        self.client.futures_change_leverage(symbol=symbol, leverage=lev)
        self.client.futures_create_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=qty
        )

        time.sleep(0.3)
        pos = self.get_open_position(symbol)
        self.long_sl.place(symbol, float(pos["entryPrice"]))

    def short(self, symbol, risk=1, lev=3):
        qty = self.calc_qty(symbol, risk, lev)
        self.client.futures_change_leverage(symbol=symbol, leverage=lev)
        self.client.futures_create_order(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=qty
        )

        time.sleep(0.3)
        pos = self.get_open_position(symbol)
        self.short_sl.place(symbol, float(pos["entryPrice"]))

# ---------------- TEST BLOCK ----------------
if __name__ == "__main__":
    print("🧪 Starting MarketOrder REAL-SL API-safety test...")

    # ✅ Central API handler (keys + IP safety + singleton)
    from api_callling.api_calling import APICall

    # ✅ REAL StopLoss engines
    from order_book.long_stop_loss import LongStopLoss
    from order_book.short_stop_loss import ShortStopLoss

    # --- Init API ---
    api = APICall()
    client = api.client

    # --- Init REAL SL engines ---
    long_sl = LongStopLoss(client)
    short_sl = ShortStopLoss(client)

    # --- MarketOrder with REAL SL ---
    trader = MarketOrder(
        client=client,
        long_sl=long_sl,
        short_sl=short_sl
    )

    print("🔍 Testing balance fetch via MarketOrder (API guarded)...")
    balance = trader.get_balance()
    print(f"✅ Balance fetched safely: {balance} USDT")

    # ❌ NO order placed here (safety test only)
