import time
from binance.exceptions import BinanceAPIException


class MarketOrder:
    def __init__(self, client):
        self.client = client

    # ============================
    # Helpers
    # ============================

    def get_open_position(self, symbol):
        pos = self.client.futures_position_information(symbol=symbol)
        for p in pos:
            if float(p["positionAmt"]) != 0:
                return p
        return None

    def get_futures_balance(self):
        data = self.client.futures_account_balance()
        for b in data:
            if b["asset"] == "USDT":
                return float(b["balance"])
        return 0.0

    def get_mark_price(self, symbol):
        return float(self.client.futures_mark_price(symbol=symbol)["markPrice"])

    def get_lot_size(self, symbol):
        info = self.client.futures_exchange_info()
        for s in info["symbols"]:
            if s["symbol"] == symbol:
                for f in s["filters"]:
                    if f["filterType"] == "LOT_SIZE":
                        return float(f["minQty"]), float(f["stepSize"])
        return 0, 0

    # ============================
    # Binance Control
    # ============================

    def set_leverage(self, symbol, leverage):
        self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
        print(f"🔧 Leverage set to {leverage}x")

    # ============================
    # Risk Engine
    # ============================

    def calculate_qty(self, symbol, risk_percent, leverage):
        balance = self.get_futures_balance()
        price = self.get_mark_price(symbol)
        min_qty, step = self.get_lot_size(symbol)

        margin = balance * risk_percent
        notional = margin * leverage
        if notional < 100:
            notional = 100

        qty = notional / price
        qty = max(qty, min_qty)
        qty = (qty // step) * step
        return float(f"{qty:.8f}")

    # ============================
    # Stop-Loss (Hedge-mode safe, dynamic)
    # ============================

    def place_stop_loss(self, symbol, entry_price, percent=0.02):
        pos = self.get_open_position(symbol)
        if not pos:
            print("❌ No open position for stop-loss")
            return

        position_amt = float(pos["positionAmt"])

        if position_amt > 0:  # LONG
            side = "SELL"
            stop_price = entry_price * (1 - percent)
        else:  # SHORT
            side = "BUY"
            stop_price = entry_price * (1 + percent)

        try:
            self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="STOP_MARKET",
                stopPrice=round(stop_price, 2),
                closePosition=True
            )
            print(f"🛑 Stop-Loss placed at {stop_price:.2f}")
        except Exception as e:
            print("❌ Stop-Loss failed:", e)

    # ============================
    # LONG (BUY)
    # ============================

    def long(self, symbol, risk_percent=1, leverage=3):
        if self.get_open_position(symbol):
            print("⚠ Position already open")
            return

        self.set_leverage(symbol, leverage)
        qty = self.calculate_qty(symbol, risk_percent, leverage)

        self.client.futures_create_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=qty
        )

        time.sleep(0.3)
        pos = self.get_open_position(symbol)
        entry_price = float(pos["entryPrice"])

        print(f"✅ LONG {qty} BTC at {entry_price}")
        self.place_stop_loss(symbol, entry_price, 0.02)

    # ============================
    # SHORT (SELL)
    # ============================

    def short(self, symbol, risk_percent=1, leverage=3):
        if self.get_open_position(symbol):
            print("⚠ Position already open")
            return

        self.set_leverage(symbol, leverage)
        qty = self.calculate_qty(symbol, risk_percent, leverage)

        self.client.futures_create_order(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=qty
        )

        time.sleep(0.3)
        pos = self.get_open_position(symbol)
        entry_price = float(pos["entryPrice"])

        print(f"🔻 SHORT {qty} BTC at {entry_price}")
        self.place_stop_loss(symbol, entry_price, 0.02)


# ============================
# Test
# ============================

if __name__ == "__main__":
    from api_callling.api_calling import APICall

    api = APICall()
    trader = MarketOrder(api.client)

    print("Balance:", trader.get_futures_balance())
    print("Price:", trader.get_mark_price("BTCUSDT"))

    # trader.long("BTCUSDT", risk_percent=1, leverage=3)
    trader.short("BTCUSDT", risk_percent=1, leverage=3)
