import asyncio
import json
import websockets

from api_callling.api_calling import APICall

# ================= BINANCE CLIENT =================
api = APICall()
client = api.client

SYMBOL_UPPER = "BTCUSDT"
SYMBOL = "btcusdt"

# ================= POSITION STATE =================
position_entry = None
position_side = None
price_peak = None


# ================= GET OPEN ORDERS =================
def get_position_orders():
    orders = client.futures_get_open_orders(symbol=SYMBOL_UPPER)

    results = []
    for o in orders:
        results.append({
            "orderId": o["orderId"],
            "type": o["type"],
            "side": o["side"],
            "price": o["price"],
            "stopPrice": o["stopPrice"],
            "status": o["status"]
        })

    return results


# ================= GET CURRENT POSITION =================
def get_position():
    positions = client.futures_position_information(symbol=SYMBOL_UPPER)

    for p in positions:
        amt = float(p["positionAmt"])
        if amt != 0:
            return {
                "side": "LONG" if amt > 0 else "SHORT",
                "entry": float(p["entryPrice"]),
                "qty": abs(amt)
            }
    return None

def update_trailing_stop(side, peak_price):
    trail_pct = 0.02   # 2%

    # Calculate new stop
    if side == "LONG":
        stop_price = round(peak_price * (1 - trail_pct), 2)
        close_side = "SELL"
    else:
        stop_price = round(peak_price * (1 + trail_pct), 2)
        close_side = "BUY"

    # Cancel existing stops
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

    # Place new stop
    client.futures_create_order(
        symbol=SYMBOL_UPPER,
        side=close_side,
        type="STOP_MARKET",
        stopPrice=stop_price,
        closePosition=True
    )

    print(f"🛑 New STOP placed at {stop_price}")

# def has_existing_stop():
    # orders = client.futures_get_open_orders(symbol=SYMBOL_UPPER)
    # for o in orders:
    #     if o["type"] in [
    #         "STOP_MARKET",
    #         "TAKE_PROFIT_MARKET",
    #         "STOP",
    #         "TAKE_PROFIT",
    #         "TRAILING_STOP_MARKET"
    #     ]:
    #         return True
    # return False


# ================= PRICE EVENT =================
async def on_price_change(price):
    global position_entry, position_side, price_peak

    print("🚨 PRICE:", price)

    pos = get_position()

    # No open trade
    if not pos:
        print("No open position")
        position_entry = None
        price_peak = None
        return

    # Lock entry price once
    if position_entry is None:
        position_entry = pos["entry"]
        position_side = pos["side"]
        price_peak = pos["entry"]
        print(f"📌 {position_side} ENTRY: {position_entry}")

        # initial protection (only if no stop exists)
        # update_trailing_stop(position_side, price_peak)
        # if not has_existing_stop():
        #     update_trailing_stop(position_side, price_peak)
        # else:
        #     print("ℹ️ Existing STOP found — initial stop skipped")

    # Track peak
    if position_side == "LONG":
        if price > price_peak:
            price_peak = price
            print(f"🚀 New HIGH → {price_peak}")
            update_trailing_stop("LONG", price_peak)
    else:
        if price < price_peak:
            price_peak = price
            print(f"📉 New LOW → {price_peak}")
            update_trailing_stop("SHORT", price_peak)

    # ==================================================
    # 3. 👉 PUT YOUR PROFIT BLOCK HERE 👈
    # ==================================================

    # Live profit (can be negative)
    live_profit = (
        (price - position_entry) / position_entry
        if position_side == "LONG"
        else (position_entry - price) / position_entry
    )

    # Trailing / locked profit (never decreases)
    trail_profit = (
        (price_peak - position_entry) / position_entry
        if position_side == "LONG"
        else (position_entry - price_peak) / position_entry
    )

    print(
        f"{position_side} | Entry {position_entry} | "
        f"Current {price} | "
        f"Peak {price_peak} | "
        f"Live PnL {live_profit*100:.2f}% | "
        f"Locked {trail_profit*100:.2f}%"
    )

    # Show active Binance orders
    orders = get_position_orders()
    if orders:
        print("📦 Active Orders:")
        for o in orders:
            print(
                f"ID={o['orderId']} | {o['type']} | {o['side']} | "
                f"Stop={o['stopPrice']} | Status={o['status']}"
            )
    else:
        print("ℹ️ The current price is below the highest recorded peak, so no new trailing stop order is needed at the moment.")


# ================= WEBSOCKET ENGINE =================
async def price_watcher():
    url = f"wss://fstream.binance.com/ws/{SYMBOL}@markPrice"

    async with websockets.connect(url) as ws:
        print("Connected to Binance WebSocket")

        last_price = None

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            price = float(data["p"])

            if last_price is None:
                last_price = price
                continue

            if price != last_price:
                await on_price_change(price)
                last_price = price


# ================= RUN =================
if __name__ == "__main__":
    asyncio.run(price_watcher())
