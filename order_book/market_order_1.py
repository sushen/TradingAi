"""
market_order.py

This module implements the Entry Engine of the TradingAI Futures system.

It is responsible ONLY for opening positions on Binance Futures.
It does not calculate or place stop-loss orders by itself.
After a position is opened, it delegates risk protection to either
LongStopLoss or ShortStopLoss.

Components:
    - Binance Futures client (self.client)
    - LongStopLoss engine (self.long_sl)
    - ShortStopLoss engine (self.short_sl)

Core Responsibilities:
    1. Read account balance
    2. Read current market price
    3. Calculate correct position size based on:
        - Account balance
        - Risk percentage
        - Leverage
        - Exchange LOT_SIZE rules
    4. Open a MARKET order (BUY for long, SELL for short)
    5. Fetch the filled entry price from open positions
    6. Pass the entry price to the appropriate StopLoss engine

LONG flow:
    - Calculate quantity
    - Set leverage
    - Send MARKET BUY
    - Read entry price
    - Call LongStopLoss.place(symbol, entry_price)

SHORT flow:
    - Calculate quantity
    - Set leverage
    - Send MARKET SELL
    - Read entry price
    - Call ShortStopLoss.place(symbol, entry_price)

Design principle:
    Entry logic and Risk logic are completely separated.
    This prevents stop-loss failures from breaking market execution
    and makes the trading engine safe and maintainable.
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import time
import winsound
from binance.exceptions import BinanceAPIException

def alert_ip_change():
    for _ in range(3):
        winsound.Beep(1000, 500)  # frequency, duration
        time.sleep(0.2)

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
                    print("🔐 IP CHANGED / API BLOCKED")
                    print("👉 Please update IP whitelist in Binance")
                    alert_ip_change()

                    input("⏸️ IP ঠিক করে ENTER চাপুন...")
                    print("🔁 Rechecking balance...")
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
        self.client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=qty)

        time.sleep(0.3)
        pos = self.get_open_position(symbol)
        self.long_sl.place(symbol, float(pos["entryPrice"]))

    def short(self, symbol, risk=1, lev=3):
        qty = self.calc_qty(symbol, risk, lev)
        self.client.futures_change_leverage(symbol=symbol, leverage=lev)
        self.client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=qty)

        time.sleep(0.3)
        pos = self.get_open_position(symbol)
        self.short_sl.place(symbol, float(pos["entryPrice"]))

if __name__ == "__main__":
    print("🧪 Starting MarketOrder API-safety test...")

    # ✅ Central API handler (ALL safety lives here)
    from api_callling.api_calling import APICall

    api = APICall()          # handles keys, IP guard, retries
    client = api.client      # safe, shared Binance client

    # 🧪 Dummy StopLoss placeholders (not used here)
    class DummySL:
        def place(self, *args, **kwargs):
            print("🛡️ Dummy SL called")

    long_sl = DummySL()
    short_sl = DummySL()

    # 🚀 Inject SAFE API client into MarketOrder
    trader = MarketOrder(
        client=client,
        long_sl=long_sl,
        short_sl=short_sl
    )

    print("🔍 Testing balance fetch via MarketOrder (API guarded)...")
    balance = trader.get_balance()

    print(f"✅ Balance fetched safely: {balance} USDT")

