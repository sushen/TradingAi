import time
import asyncio
import threading
from binance import AsyncClient, BinanceSocketManager


class SafeEntry:
    """
    SAFE ENTRY — Bottom/Top Based Confirmation (ASYNC, THREAD-SAFE)
    --------------------------------------------------------------
    LONG  → price goes DOWN → store BOTTOM → recover %
    SHORT → price goes UP   → store TOP    → drop %

    - Runs its own asyncio loop in a daemon thread
    - Safe to call from synchronous main.py
    - NO order execution
    """

    def __init__(
        self,
        symbol: str,
        safe_distance_pct: float = 0.001,
        confirm_ticks: int = 1,
        max_wait: int = 240,
        min_tick: float = 0.05,
    ):
        self.symbol = symbol.lower()
        self.safe_distance_pct = safe_distance_pct
        self.confirm_ticks = confirm_ticks
        self.max_wait = max_wait
        self.min_tick = min_tick

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

    # ==================================================
    # PUBLIC API
    # ==================================================

    def long(self):
        self._start("LONG")

    def short(self):
        self._start("SHORT")

    # ==================================================
    # START (THREAD + EVENT LOOP)
    # ==================================================

    def _start(self, side: str):
        if self.active:
            print("⚠ Safe Entry already active", flush=True)
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

        print(f"🔐 Safe Entry STARTED | {side}", flush=True)

        # 🔥 FIX: run asyncio in its own daemon thread
        threading.Thread(
            target=self._run_thread,
            daemon=True
        ).start()

    def _run_thread(self):
        asyncio.run(self._run())

    # ==================================================
    # WEBSOCKET LOOP
    # ==================================================

    async def _run(self):
        client = await AsyncClient.create()
        bsm = BinanceSocketManager(client)

        try:
            async with bsm.symbol_ticker_socket(self.symbol) as stream:
                while self.active:
                    msg = await stream.recv()
                    await self._on_price(msg)
        finally:
            await client.close_connection()

    # ==================================================
    # PRICE HANDLER
    # ==================================================

    async def _on_price(self, msg):
        if not self.active or self.confirmed or self.timed_out:
            return

        try:
            price = float(msg["c"])
        except Exception:
            return

        # NOISE FILTER
        if self.last_price is not None:
            if abs(price - self.last_price) < self.min_tick:
                return

        print(f"📈 Live price → {price}", flush=True)

        # First tick
        if self.start_price is None:
            self.start_price = price
            self.bottom_price = price
            self.top_price = price
            self.last_price = price
            print(f"📍 Start price → {price}", flush=True)
            return

        # Timeout
        if time.time() - self.start_time > self.max_wait:
            print("⏱ Safe Entry TIMEOUT", flush=True)
            self.timed_out = True
            self.active = False
            return

        # ================= LONG =================
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

        # ================= SHORT =================
        elif self.side == "SHORT":

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

        # CONFIRM
        if self.confirm_count >= self.confirm_ticks:
            self.confirmed = True
            self.active = False
            print(f"✅ SAFE ENTRY CONFIRMED @ {price}", flush=True)
