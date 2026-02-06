import os
import sys
import time
import threading
import re

# ---------------- PATH FIX ----------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from order_book.cancel_orders import ConditionalOrderCanceller
from sounds.sound_engine import SoundEngine
from ip_address.ip_address import (
    PublicIPResolver,
    _load_manual_whitelist,
    DEFAULT_MANUAL_WHITELIST_FILE,
    DEFAULT_MANUAL_WHITELIST_ENV,
    DEFAULT_MANUAL_WHITELIST_CACHE_TTL_SECONDS,
)

sound = SoundEngine()

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

        # state
        self.entry_price = None
        self.side = None
        self.peak_price = None
        self.last_stop_price = None

        self.cleaned_after_close = False
        self.no_position_logged = False
        self._ip_beep_active = False
        self.BEEP_DURATION_SECONDS = 600
        self.BEEP_INTERVAL_SECONDS = 4.0
        self._manual_whitelist = set()
        self._manual_whitelist_last_load = 0.0
        self._manual_whitelist_ttl = DEFAULT_MANUAL_WHITELIST_CACHE_TTL_SECONDS

    def _is_ip_whitelist_error(self, exc):
        code = getattr(exc, "code", None)
        if code == -2015:
            return True
        msg = str(exc)
        return (
            "code=-2015" in msg
            or "Invalid API-key, IP, or permissions" in msg
        )

    def _extract_request_ip(self, exc):
        msg = str(exc)
        match = re.search(r"request ip:\s*([0-9a-fA-F\.:]+)", msg)
        if match:
            return match.group(1)
        return None

    def _get_public_ip(self):
        try:
            ips = PublicIPResolver().fetch()
            return ips.get("ipv4") or ips.get("ipv6")
        except Exception:
            return None

    def _get_manual_whitelist(self):
        now = time.time()
        if now - self._manual_whitelist_last_load < self._manual_whitelist_ttl:
            return set(self._manual_whitelist)

        file_path = os.environ.get(
            "BINANCE_MANUAL_WHITELIST_FILE",
            DEFAULT_MANUAL_WHITELIST_FILE,
        )
        manual_ips = _load_manual_whitelist(DEFAULT_MANUAL_WHITELIST_ENV, file_path)
        self._manual_whitelist = manual_ips
        self._manual_whitelist_last_load = now
        return set(manual_ips)

    def _should_beep_for_ip(self, ip_value):
        if not ip_value:
            return True
        return ip_value not in self._get_manual_whitelist()

    def _start_ip_beep(self, ip_value=None):
        if not self._should_beep_for_ip(ip_value):
            return
        if self._ip_beep_active:
            return
        self._ip_beep_active = True

        def _worker():
            try:
                end_time = time.time() + self.BEEP_DURATION_SECONDS
                while time.time() < end_time:
                    sound.beep(repeat=1, delay=0.0)
                    time.sleep(self.BEEP_INTERVAL_SECONDS)
            finally:
                self._ip_beep_active = False

        threading.Thread(target=_worker, daemon=True).start()

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

    # ---------- PNL & ROI ----------
    def calc_peak_roi(self, pos):
        pnl_peak = (
            pos["qty"] * (self.peak_price - pos["entry"])
            if pos["side"] == "LONG"
            else pos["qty"] * (pos["entry"] - self.peak_price)
        )

        base = pos["margin"] if pos["margin"] > 0 else pos["entry"] * pos["qty"]
        return pnl_peak / base if base > 0 else 0.0

    def calc_pnl_and_roi(self, pos, price):
        pnl = (
            pos["qty"] * (price - pos["entry"])
            if pos["side"] == "LONG"
            else pos["qty"] * (pos["entry"] - price)
        )

        base = pos["margin"] if pos["margin"] > 0 else pos["entry"] * pos["qty"]
        roi = pnl / base if base > 0 else 0.0

        return pnl, roi

    # ---------- PEAK ROI → PRICE ----------

    def price_from_peak_roi(self, pos, roi_from_peak):
        delta = roi_from_peak * (pos["margin"] / pos["qty"])
        return (
            self.peak_price + delta
            if pos["side"] == "LONG"
            else self.peak_price - delta
        )

    # ---------- STOP CONTROL ----------

    def place_stop(self, pos, stop, roi):
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
        print(f"🛑 STOP SET → {stop} | ROI {roi * 100:.2f}%")

    # ---------- MAIN LOOP ----------

    def run(self):
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
                    self.no_position_logged = False
                    self.entry_price = pos["entry"]
                    self.side = pos["side"]
                    self.peak_price = price
                    self.last_stop_price = None
                    print(f"📌 {self.side} ENTRY @ {self.entry_price:.2f}")

                # ===== PEAK TRACK =====
                if pos["side"] == "LONG":
                    self.peak_price = max(self.peak_price, price)
                else:
                    self.peak_price = min(self.peak_price, price)

                # ===== CALC =====
                pnl, roi = self.calc_pnl_and_roi(pos, price)

                # ===== PEAK ROI STOP =====
                stop = self.price_from_peak_roi(pos, PEAK_ROI_STOP)

                if (
                    self.last_stop_price is None
                    or abs(stop - self.last_stop_price) >= MIN_STOP_MOVE
                ):
                    self.place_stop(pos, stop, roi)

                # ===== INFO PRINT =====
                peak_roi = self.calc_peak_roi(pos)
                now = time.strftime("%H:%M:%S")
                last_sl_display = (
                    f"{self.last_stop_price:.2f}"
                    if self.last_stop_price is not None
                    else "--"
                )
                side_label = "L" if self.side == "LONG" else "S"

                print(
                    f"{now} | "
                    f"{side_label} | "
                    f"Entry {self.entry_price:.2f} | "
                    f"CP {price:.2f} | "
                    f"Peak {self.peak_price:.2f} | "
                    f"LastSL {last_sl_display} | "
                    f"PNL {pnl:.2f} USDT | "
                    f"ROI {roi * 100:.2f}% | "
                    f"PROI {peak_roi * 100:.2f}%"
                )

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("❌ Engine error:", e)
                if self._is_ip_whitelist_error(e):
                    ip_value = self._extract_request_ip(e) or self._get_public_ip()
                    if self._should_beep_for_ip(ip_value):
                        print("⚠️ IP not whitelisted. Sound alert triggered.")
                        self._start_ip_beep(ip_value)
                time.sleep(3)

    # ---------- LIFECYCLE ----------

    def start(self):
        if self.running:
            return

        self.running = True
        threading.Thread(target=self.run, daemon=True).start()


# ================= STANDALONE =================

if __name__ == "__main__":
    from api_callling.api_calling import APICall

    ConditionalOrderCanceller(symbol=SYMBOL).cancel_all()

    api = APICall()
    client = api.client

    engine = ProgressiveTrailingStop(client)
    engine.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Engine stopped")
