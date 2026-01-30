# risk_management/safe_entry.py

import time
import threading
import requests


class SafeEntry:
    """
    SAFE ENTRY — Bottom / Top Based Confirmation
    --------------------------------------------
    MODES:
    1) Injected Binance client (PRODUCTION)
    2) Standalone PUBLIC REST with fallback endpoints

    Designed for restricted / slow networks.
    """

    PUBLIC_ENDPOINTS = [
        # Futures
        ("https://fapi.binance.com/fapi/v1/ticker/price", "price"),
        # Spot fallback
        ("https://api.binance.com/api/v3/ticker/price", "price"),
    ]

    def __init__(
        self,
        client=None,
        symbol: str = "BTCUSDT",
        safe_distance_pct: float = 0.005,
        confirm_ticks: int = 2,
        max_wait: int = 14720,
        min_tick: float = 0.05,
        poll_interval: float = 0.5,
    ):
        self.client = client
        self.symbol = symbol.upper()

        self.safe_distance_pct = safe_distance_pct
        self.confirm_ticks = confirm_ticks
        self.max_wait = max_wait
        self.min_tick = min_tick
        self.poll_interval = poll_interval

        # state
        self.side = None
        self.start_price = None
        self.bottom_price = None
        self.top_price = None
        self.last_price = None
        self.confirm_count = 0
        self.start_time = None

        self.active = False
        self.confirmed = False
        self.timed_out = False

    # ================= PUBLIC =================

    def long(self):
        self._start("LONG")

    def short(self):
        self._start("SHORT")

    # ================= INTERNAL =================

    def _start(self, side: str):
        if self.active:
            print("⚠ SafeEntry already active", flush=True)
            return

        self.side = side
        self.start_price = None
        self.bottom_price = None
        self.top_price = None
        self.last_price = None
        self.confirm_count = 0
        self.start_time = time.time()

        self.active = True
        self.confirmed = False
        self.timed_out = False

        mode = "PRODUCTION (client)" if self.client else "STANDALONE (public REST)"
        print(f"🔐 Safe Entry STARTED | {side} | {mode}", flush=True)

        threading.Thread(target=self._run, daemon=True).start()

    def _get_price_public(self):
        """
        Try multiple public endpoints with short timeout.
        """
        for url, key in self.PUBLIC_ENDPOINTS:
            try:
                r = requests.get(
                    url,
                    params={"symbol": self.symbol},
                    timeout=3
                )
                r.raise_for_status()
                return float(r.json()[key])
            except Exception:
                continue

        raise ConnectionError("All public endpoints failed")

    def _get_price(self):
        if self.client:
            data = self.client.futures_mark_price(symbol=self.symbol)
            return float(data["markPrice"])

        return self._get_price_public()

    def _run(self):
        while self.active:
            try:
                price = self._get_price()
                self._on_price(price)
            except Exception as e:
                print(f"⚠ SafeEntry price fetch failed: {e}", flush=True)

            time.sleep(self.poll_interval)

    def _on_price(self, price: float):
        if not self.active or self.confirmed or self.timed_out:
            return

        if self.last_price is not None:
            if abs(price - self.last_price) < self.min_tick:
                return

        print(f"📈 Price → {price}", flush=True)

        if self.start_price is None:
            self.start_price = price
            self.bottom_price = price
            self.top_price = price
            self.last_price = price
            print(f"📍 Start price → {price}", flush=True)
            return

        if time.time() - self.start_time > self.max_wait:
            print("⏱ SafeEntry TIMEOUT", flush=True)
            self.timed_out = True
            self.active = False
            return

        # ---------- LONG ----------
        if self.side == "LONG":
            if price < self.bottom_price:
                self.bottom_price = price
                self.confirm_count = 0
                print(f"🔻 New bottom → {price}", flush=True)

            trigger = self.bottom_price * (1 + self.safe_distance_pct)

            if price >= trigger:
                self.confirm_count += 1
                print(
                    f"🔁 Recovery {self.confirm_count}/{self.confirm_ticks} | "
                    f"Trigger → {round(trigger, 2)}",
                    flush=True
                )
            else:
                self.confirm_count = 0

        # ---------- SHORT ----------
        else:
            if price > self.top_price:
                self.top_price = price
                self.confirm_count = 0
                print(f"🔺 New top → {price}", flush=True)

            trigger = self.top_price * (1 - self.safe_distance_pct)

            if price <= trigger:
                self.confirm_count += 1
                print(
                    f"🔁 Drop {self.confirm_count}/{self.confirm_ticks} | "
                    f"Trigger → {round(trigger, 2)}",
                    flush=True
                )
            else:
                self.confirm_count = 0

        self.last_price = price

        if self.confirm_count >= self.confirm_ticks:
            self.confirmed = True
            self.active = False
            print(f"✅ SAFE ENTRY CONFIRMED @ {price}", flush=True)


# ==================================================
# STANDALONE RUN
# ==================================================

if __name__ == "__main__":
    print("🧪 Running SafeEntry in STANDALONE mode (resilient public REST)")

    se = SafeEntry(
        symbol="BTCUSDT",
        safe_distance_pct=0.005,
        confirm_ticks=2,
        min_tick=0.05,
    )

    se.long()

    while se.active:
        time.sleep(0.5)

    if se.confirmed:
        print("🎯 Entry confirmed — ready to place order")
    elif se.timed_out:
        print("❌ Entry timed out")
