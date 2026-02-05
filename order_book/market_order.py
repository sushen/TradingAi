import os
import os
import sys
import time
import threading

from binance.exceptions import BinanceAPIException
from sounds.sound_engine import SoundEngine

sound = SoundEngine()

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
        sound.beep(2, 1)
        time.sleep(1.5)

# ---------------- MARKET ORDER ENGINE ----------------
class MarketOrder:
    def __init__(self, client, long_sl, short_sl, on_alert=None):
        self.client = client
        self.long_sl = long_sl
        self.short_sl = short_sl
        self.on_alert = on_alert
        # Aggressive mode: use a short-lived cached balance if API hiccups.
        self._balance_cache = None
        self._balance_cache_ts = None
        self.BALANCE_CACHE_TTL = 120
        self._ip_alert_active = False
        self._ip_alert_stop_flag = None
        self._ip_alert_thread = None

    def _start_ip_alert(self):
        if self._ip_alert_active:
            return

        self._ip_alert_stop_flag = {"stop": False}
        self._ip_alert_thread = threading.Thread(
            target=alert_ip_change_loop,
            args=(self._ip_alert_stop_flag,),
            daemon=True
        )
        self._ip_alert_thread.start()
        self._ip_alert_active = True

        sound.ip_not_whitelisted()
        sound.voice_alert(
            "Your IP is not whitelisted in Binance. "
            "Please add it to the whitelist. "
            "Alert will continue until the IP is whitelisted."
        )
        if self.on_alert:
            self.on_alert(
                "IP changed / not whitelisted. Update Binance whitelist.",
                "red"
            )

    def _stop_ip_alert(self):
        if not self._ip_alert_active:
            return

        if self._ip_alert_stop_flag is not None:
            self._ip_alert_stop_flag["stop"] = True
        self._ip_alert_active = False
        self._ip_alert_stop_flag = None
        self._ip_alert_thread = None
        sound.reset("IP_NOT_WHITELISTED")
        if self.on_alert:
            self.on_alert("IP whitelist OK. Trading resumes.", "green")

    def get_open_position(self, symbol):
        pos = self.client.futures_position_information(symbol=symbol)
        for p in pos:
            if float(p["positionAmt"]) != 0:
                return p
        return None

    def get_balance(self):
        retries = 5
        base_delay = 2

        if (
            self._balance_cache is not None
            and self._balance_cache_ts is not None
            and (time.monotonic() - self._balance_cache_ts) <= self.BALANCE_CACHE_TTL
        ):
            print("⚡ Using cached balance (fast path).", flush=True)
            return self._balance_cache

        for attempt in range(1, retries + 1):
            try:
                for b in self.client.futures_account_balance():
                    if b["asset"] == "USDT":
                        balance = float(b["balance"])
                        self._balance_cache = balance
                        self._balance_cache_ts = time.monotonic()
                        self._stop_ip_alert()
                        return balance

            except BinanceAPIException as e:
                if e.code == -2015:
                    print("\nIP CHANGED / API BLOCKED")
                    print("Please update IP whitelist in Binance")
                    print("Alert will continue until the IP is whitelisted")

                    self._start_ip_alert()
                    time.sleep(base_delay * attempt)
                    continue

                print(f"⚠ Binance API error: {e}", flush=True)

            except Exception as e:
                print(
                    f"⚠ Balance fetch failed ({attempt}/{retries}): {e}",
                    flush=True
                )

            time.sleep(base_delay * attempt)

        if (
            self._balance_cache is not None
            and self._balance_cache_ts is not None
            and (time.monotonic() - self._balance_cache_ts) <= self.BALANCE_CACHE_TTL
        ):
            print("⚠ Using cached balance (API unstable).", flush=True)
            return self._balance_cache

        raise RuntimeError("❌ Unable to fetch futures balance after retries")

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
        if pos is None:
            raise RuntimeError("❌ Unable to read open position after order")

        entry_price = float(pos["entryPrice"])
        print(f"✅ Entry price → {entry_price}", flush=True)
        self.long_sl.place(symbol, entry_price)

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
        if pos is None:
            raise RuntimeError("❌ Unable to read open position after order")

        entry_price = float(pos["entryPrice"])
        print(f"✅ Entry price → {entry_price}", flush=True)
        self.short_sl.place(symbol, entry_price)

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
