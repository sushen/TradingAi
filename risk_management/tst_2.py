import asyncio
import json
import websockets

from api_callling.api_calling import APICall

# ================= BINANCE CLIENT =================
api = APICall()
client = api.client

SYMBOL_UPPER = "BTCUSDT"
SYMBOL = "btcusdt"

# ================= PROFIT → TRAILING TIERS =================
PROFIT_TIERS = [
    (0.10, 0.005),   # 10%+ → 0.5%
    (0.05, 0.01),    # 5%+ → 1%
    (0.00, 0.02)    # default
]

def trailing_percent(profit):
    for level, percent in PROFIT_TIERS:
        if profit >= level:
            return percent
    return 0.02


# ================= POSITION STATE =================
position_entry = None
position_side = None
price_peak = None


# ================= POSITION INFO (WITH LEVERAGE) =================
def get_position():
    positions = client.futures_position_information(symbol=SYMBOL_UPPER)

    for p in positions:
        amt = float(p["positionAmt"])
        if amt != 0:
            return {
                "side": "LONG" if amt > 0 else "SHORT",
                "entry": float(p["entryPrice"]),
                "qty": abs(amt),
                "leverage": float(p.get("leverage", 1))
            }
    return None


# ================= TRAILING STOP =================
def update_trailing_stop(side, peak_price, trail_pct):
    if side == "LONG":
        stop_price = round(peak_price * (1 - trail_pct), 2)
        close_side = "SELL"
    else:
        stop_price = round(peak_price * (1 + trail_pct), 2)
        close_side = "BUY"

    # Cancel ALL stop-type orders (Binance GTE rule)
    orders = client.futures_get_open_orders(symbol=SYMBOL_UPPER)
    for o in orders:
        if o["type"] in [
            "STOP_MARKET",
            "TAKE_PROFIT_MARKET",
            "STOP",
            "TAKE_PROFIT",
            "TRAILING_STOP_MARKET"
        ]:
            client.futures_cancel_order(
                symbol=SYMBOL_UPPER,
                orderId=o["orderId"]
            )

    client.futures_create_order(
        symbol=SYMBOL_UPPER,
        side=close_side,
        type="STOP_MARKET",
        stopPrice=stop_price,
        closePosition=True
    )

    print(f"🛑 New STOP placed at {stop_price} | Trail {trail_pct*100:.2f}%")


# ================= PRICE EVENT =================
async def on_price_change(price):
    global position_entry, position_side, price_peak

    pos = get_position()
    if not pos:
        position_entry = None
        price_peak = None
        return

    # Lock entry
    if position_entry is None:
        position_entry = pos["entry"]
        position_side = pos["side"]
        price_peak = pos["entry"]
        print(f"📌 {position_side} ENTRY: {position_entry}")

    # Update peak
    if position_side == "LONG" and price > price_peak:
        price_peak = price
        print(f"🚀 New HIGH → {price_peak}")

    elif position_side == "SHORT" and price < price_peak:
        price_peak = price
        print(f"📉 New LOW → {price_peak}")

    # Profit (price based)
    profit = (
        (price_peak - position_entry) / position_entry
        if position_side == "LONG"
        else (position_entry - price_peak) / position_entry
    )

    trail_pct = trailing_percent(profit)

    # Update trailing stop ONLY after peak move
    if (
        (position_side == "LONG" and price == price_peak) or
        (position_side == "SHORT" and price == price_peak)
    ):
        update_trailing_stop(position_side, price_peak, trail_pct)

    # Live profit & ROI
    live_profit = (
        (price - position_entry) / position_entry
        if position_side == "LONG"
        else (position_entry - price) / position_entry
    )

    live_roi = live_profit * pos["leverage"]
    locked_roi = profit * pos["leverage"]

    print(
        f"{position_side} | Entry {position_entry} | "
        f"Current {price} | Peak {price_peak} | "
        f"Live ROI {live_roi*100:.2f}% | "
        f"Locked ROI {locked_roi*100:.2f}% | "
        f"Lev {pos['leverage']}x"
    )


# ================= WEBSOCKET =================
async def price_watcher():
    url = f"wss://fstream.binance.com/ws/{SYMBOL}@markPrice"

    async with websockets.connect(url) as ws:
        print("🚀 Connected to Binance WebSocket")

        last_price = None

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            price = float(data["p"])

            if price != last_price:
                await on_price_change(price)
                last_price = price


# ================= RUN =================
if __name__ == "__main__":
    asyncio.run(price_watcher())
