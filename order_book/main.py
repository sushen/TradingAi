"""
main.py

This is the execution entry point of the TradingAI Futures system.

This file does not contain any trading logic.
It only wires together the core components:

    - APICall        → Binance Futures API connection
    - MarketOrder   → Position entry engine
    - LongStopLoss  → Risk manager for LONG positions
    - ShortStopLoss → Risk manager for SHORT positions

Architecture:
    Entry and Risk are fully separated.

    MarketOrder handles:
        - Opening LONG and SHORT positions using MARKET orders

    LongStopLoss and ShortStopLoss handle:
        - Placing STOP_MARKET orders to protect open positions

Execution Flow:
    1. Create a shared Binance API client (APICall)
    2. Inject the client into both stop-loss engines
    3. Inject both stop-loss engines into MarketOrder
    4. Call trader.long() or trader.short() to execute a trade

This design ensures:
    - Entry logic is never affected by stop-loss failures
    - LONG and SHORT risk management are isolated
    - The system is safe, modular, and production-ready
"""

from api_callling.api_calling import APICall
from market_order import MarketOrder
from long_stop_loss import LongStopLoss
from short_stop_loss import ShortStopLoss

api = APICall()

long_sl = LongStopLoss(api.client)
short_sl = ShortStopLoss(api.client)

trader = MarketOrder(api.client, long_sl, short_sl)

# trader.long("BTCUSDT", 1, 4)
trader.short("BTCUSDT", 1, 4)
