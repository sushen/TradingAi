import random
import sqlite3
import requests
from api_callling.api_calling import APICall


# ===== INIT BINANCE (YOUR SYSTEM) =====
api = APICall()
client = api.client   # ← this is the SAME Binance client from api_calling.py

url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
data = requests.get(url).json()

current_price = float(data["price"])
print("Current BTC price (Binance):", current_price)

DB_FILE = "../one_years_btc_crypto_data.db"
# Read latest price from DB
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
    SELECT Close
    FROM asset_1
    ORDER BY Time DESC
    LIMIT 1
""")

row = cursor.fetchone()
print("DB row:", row)

# previous_minute_price = random.randint(100000,105000)
previous_minute_price = float(row[0])
print("Previous minute price:", previous_minute_price)

# current_price = random.randint(95000,110000)
current_price = float(data["price"])
print("Current price:", current_price)

exponential_stop_loss = 0.02
print("Exponential stop loss:", exponential_stop_loss)

stop_loss_price = previous_minute_price * (1 - exponential_stop_loss)
print("Stop loss price:", stop_loss_price)


if current_price <= stop_loss_price:
    SYMBOL = "BTCUSDT"

    # ===== Read open futures position =====
    positions = client.futures_position_information(symbol=SYMBOL)

    position_amt = 0
    for p in positions:
        amt = float(p["positionAmt"])
        if amt != 0:
            position_amt = amt
            break

    if position_amt == 0:
        print("⚠️ No open futures position")
    else:
        print("Open position:", position_amt)

        if current_price <= stop_loss_price:
            print("🚨 STOP LOSS HIT")

            # Determine correct close side
            if position_amt > 0:
                side = "SELL"  # closing LONG
            else:
                side = "BUY"  # closing SHORT

            qty = abs(position_amt)

            print(f"🔥 MARKET CLOSE → {side} {qty}")

            order = client.futures_create_order(
                symbol=SYMBOL,
                side=side,
                type="MARKET",
                quantity=qty
            )

            print("✅ Position closed:", order)

else:
    SYMBOL = "BTCUSDT"

    # ===== read open futures position =====
    positions = client.futures_position_information(symbol=SYMBOL)

    position_amt = 0
    for p in positions:
        amt = float(p["positionAmt"])
        if amt != 0:
            position_amt = amt
            break

    if position_amt == 0:
        print("⚠️ No open position, no stop to place")
    else:
        print("🟢 HOLD — updating stop loss")

        # LONG → sell stop, SHORT → buy stop
        if position_amt > 0:
            side = "SELL"
        else:
            side = "BUY"

        qty = abs(position_amt)

        # cancel all old stop orders
        client.futures_cancel_all_open_orders(symbol=SYMBOL)

        # create new stop-loss order using your calculated stop_loss_price
        stop_order = client.futures_create_order(
            symbol=SYMBOL,
            side=side,
            type="STOP_MARKET",
            stopPrice=round(stop_loss_price, 2),
            quantity=qty,
            workingType="MARK_PRICE"
        )

        print("🛑 New stop loss placed at:", stop_loss_price)


