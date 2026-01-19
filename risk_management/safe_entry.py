import time
import asyncio
from binance import AsyncClient, BinanceSocketManager


class SafeEntry:
    """
    SAFE ENTRY — Bottom/Top Based Confirmation (ASYNCIO)
    ---------------------------------------------------
    LONG  → price goes DOWN → store BOTTOM → recover 0.15%
    SHORT → price goes UP   → store TOP    → drop 0.15%

    - Python 3.13 compatible
    - REAL-TIME ticker price
    - Noise filtered
    - NO order execution
    """

    def __init__(
        self,
        symbol: str,
        safe_distance_pct: float = 0.0015,  # 0.15%
        confirm_ticks: int = 2,
        max_wait: int = 120,
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
        self.bottom_price = None   # for LONG
        self.top_price = None      # for SHORT
        self.last_price = None
        self.confirm_count = 0
        self.start_time = None

        self.active = False
        self.confirmed = False
        self.timed_out = False
        self._task = None

    # ==================================================
    # PUBLIC API
    # ==================================================

    def long(self):
        self._start("LONG")

    def short(self):
        self._start("SHORT")

    # ==================================================
    # START
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

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._task = loop.create_task(self._run())

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

        # First price
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
            self._stop()
            return

        # ==================================================
        # LONG LOGIC (price DOWN → bottom → recover)
        # ==================================================
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

        # ==================================================
        # SHORT LOGIC (price UP → top → drop)
        # ==================================================
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
            print(f"✅ SAFE ENTRY CONFIRMED @ {price}", flush=True)
            self._stop()

    # ==================================================
    # STOP
    # ==================================================

    def _stop(self):
        self.active = False
        if self._task:
            self._task.cancel()


# ==================================================
# STANDALONE TEST
# ==================================================
if __name__ == "__main__":
    SYMBOL = "BTCUSDT"
    SIDE = "LONG"  # change to SHORT if needed

    async def main():
        safe_entry = SafeEntry(
            symbol=SYMBOL,
            safe_distance_pct=0.001,
            confirm_ticks=2,
            max_wait=240,
            min_tick=0.05,
        )

        if SIDE == "LONG":
            safe_entry.long()
        else:
            safe_entry.short()

        print("📡 Async SafeEntry running... (Ctrl+C to stop)", flush=True)

        while safe_entry.active:
            await asyncio.sleep(0.1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user", flush=True)
