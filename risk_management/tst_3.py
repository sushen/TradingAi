import asyncio
import json
import websockets

from api_callling.api_calling import APICall

# ================= BINANCE CLIENT =================
api = APICall()
client = api.client

SYMBOL = "BTCUSDT"

# ================= CONFIG =================

# ROI-based trailing tiers (Binance-margin accurate)
ROI_TIERS = [
    (0.10, 0.005),   # 10% ROI → 0.5% trail
    (0.05, 0.01),    # 5% ROI → 1% trail
    (0.00, 0.02)     # default
]

MIN_PNL_IMPROVEMENT = 0.5  # USDT (anti stop-spam)


def trailing_percent(roi):
    for level, percent in ROI_TIERS:
        if roi >= level:
            return percent
    return 0.02


# ================= POSITION STATE =================
position_side = None
price_peak = None
locked_pnl = 0.0


# ================= POSITION INFO =================
def get_position():
    positions = client.futures_position_information(symbol=SYMBOL)

    for p in positions:
        amt = float(p["positionAmt"])
        if amt != 0:
            margin = float(p.get("initialMargin", 0))

            return {
                "side": "LONG" if amt > 0 else "SHORT",
                "entry": float(p["entryPrice"]),
                "position_amt": abs(amt),
                "margin": margin,
                # SAFE access (no KeyError, no TypeError)
                "leverage": float(p.get("leverage", 1)),
            }
    return None



# ================= REAL PNL / ROI =================
def calc_pnl_and_roi(pos, price):
    entry = pos["entry"]
    amt = pos["position_amt"]
    margin = pos["margin"]
    side = pos["side"]

    pnl = (
        amt * (price - entry)
        if side == "LONG"
        else amt * (entry - price)
    )

    roi = pnl / margin if margin > 1e-8 else 0
    return pnl, roi


# ================= TRAILING STOP (CORRECT) =================
def update_trailing_stop(pos, peak_price, trail_pct):
    side = pos["side"]

    if side == "LONG":
        stop_price = round(peak_price * (1 - trail_pct), 2)
        close_side = "SELL"
    else:
        stop_price = round(peak_price * (1 + trail_pct), 2)
        close_side = "BUY"

    # Cancel existing stop-type orders (Binance rule)
    orders = client.futures_get_open_orders(symbol=SYMBOL)
    for o in orders:
        if o["type"] in (
            "STOP_MARKET",
            "TAKE_PROFIT_MARKET",
            "STOP",
            "TAKE_PROFIT",
            "TRAILING_STOP_MARKET",
        ):
            client.futures_cancel_order(
                symbol=SYMBOL,
                orderId=o["orderId"]
            )

    # Place new trailing stop
    client.futures_create_order(
        symbol=SYMBOL,
        side=close_side,
        type="STOP_MARKET",
        stopPrice=stop_price,
        closePosition=True
    )

    print(f"🛑 STOP updated → {stop_price} | Trail {trail_pct*100:.2f}%")


# ================= PRICE EVENT =================
async def on_price_change(price):
    global position_side, price_peak, locked_pnl

    pos = get_position()
    if not pos:
        position_side = None
        price_peak = None
        locked_pnl = 0.0
        return

    # Lock initial state
    if position_side is None:
        position_side = pos["side"]
        price_peak = pos["entry"]
        locked_pnl = 0.0
        print(f"📌 {position_side} ENTRY: {pos['entry']}")

    # Track peak price
    if position_side == "LONG" and price > price_peak:
        price_peak = price
    elif position_side == "SHORT" and price < price_peak:
        price_peak = price

    # Calculate real PnL & ROI
    live_pnl, live_roi = calc_pnl_and_roi(pos, price)
    peak_pnl, peak_roi = calc_pnl_and_roi(pos, price_peak)

    # Update trailing stop only on REAL improvement
    if peak_pnl > locked_pnl + MIN_PNL_IMPROVEMENT:
        locked_pnl = peak_pnl
        trail_pct = trailing_percent(peak_roi)
        update_trailing_stop(pos, price_peak, trail_pct)

    print(
        f"{position_side} | Entry {pos['entry']} | "
        f"Mark {price} | Peak {price_peak} | "
        f"PNL {live_pnl:.2f} USDT | "
        f"ROI {live_roi*100:.2f}% | "
        f"Locked ROI {(locked_pnl/pos['margin'])*100:.2f}% | "
        f"Lev {pos['leverage']}x"
    )


# ================= WEBSOCKET =================
async def price_watcher():
    url = f"wss://fstream.binance.com/ws/{SYMBOL.lower()}@markPrice"

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
