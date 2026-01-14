"""
long_stop_loss.py

This module implements the Stop-Loss engine for LONG positions
in the TradingAI Futures system.

It is responsible ONLY for protecting an already opened LONG position.
It never opens trades and never manages position sizing.

Risk Model:
    Stop Price = Entry Price × (1 − Percent)

Where:
    - Entry Price is the filled price of the MARKET BUY order
    - Percent is the allowed loss (default = 2%)

Example:
    Entry = 95,000
    Percent = 0.02
    Stop = 95,000 × 0.98 = 93,100

When the market price reaches the stop price, Binance automatically
executes a market order that closes the LONG position.

Important Binance Behavior:
    Binance Futures blocks SELL STOP_MARKET in some hedge-mode contexts.
    Therefore this module uses:
        side = BUY
        closePosition = True

    This instructs Binance to close the existing LONG position
    regardless of position size, using its internal hedge engine.

Design Principle:
    This class is a pure risk manager.
    Entry execution and stop-loss execution are intentionally separated
    to ensure system stability and reliability.
"""

class LongStopLoss:
    def __init__(self, client, percent=0.02):
        self.client = client
        self.percent = percent

    def place(self, symbol, entry):
        stop = round(entry * (1 - self.percent), 2)

        self.client.futures_create_order(
            symbol=symbol,
            side="SELL",
            type="STOP_MARKET",
            stopPrice=stop,
            closePosition=True,
            workingType="MARK_PRICE"
        )

        print(f"🛑 LONG Stop set at {stop}")


