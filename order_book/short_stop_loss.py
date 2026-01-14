"""
short_stop_loss.py

This module implements the Stop-Loss engine for SHORT positions
in the TradingAI Futures system.

It is responsible only for protecting an already opened SHORT position.
It never opens trades and never manages position sizing.

Risk Model:
    Stop Price = Entry Price × (1 + Percent)

Where:
    - Entry Price is the filled price of the MARKET SELL order
    - Percent is the allowed loss (default = 2%)

Example:
    Entry = 95,000
    Percent = 0.02
    Stop = 95,000 × 1.02 = 96,900

When the market price rises to the stop price, Binance automatically
executes a market order that closes the SHORT position.

Binance Execution Model:
    This module uses:
        side = BUY
        type = STOP_MARKET
        closePosition = True

    This instructs Binance to buy back the position and fully close
    the existing SHORT, regardless of position size.

Design Principle:
    This class is a pure risk-management engine.
    It is intentionally separated from entry logic so that
    SHORT risk handling never interferes with trade execution.
"""

class ShortStopLoss:
    def __init__(self, client, percent=0.02):
        self.client = client
        self.percent = percent

    def place(self, symbol, entry):
        stop = round(entry * (1 + self.percent), 2)

        self.client.futures_create_order(
            symbol=symbol,
            side="BUY",
            type="STOP_MARKET",
            stopPrice=stop,
            closePosition=True,
            workingType="MARK_PRICE"
        )

        print(f"🛑 SHORT Stop set at {stop}")

