import time
import requests
import hmac
import hashlib
import urllib.parse
from api_callling.api_calling import APICall
from requests.exceptions import ConnectionError, ReadTimeout

SYMBOL = "BTCUSDT"
BASE_URL = "https://fapi.binance.com"

STOP_TYPES = (
    "STOP_MARKET",
    "TAKE_PROFIT_MARKET",
    "STOP",
    "TAKE_PROFIT"
)

# ===== API INIT (USING YOUR CLASS) =====
try:
    api = APICall()
    client = api.client
    api_key = api.api_key
    api_secret = api.api_secret
except Exception as e:
    print("🚫 API INIT FAILED:", e)
    exit(0)

headers = {"X-MBX-APIKEY": api_key}

def sign(params: dict):
    query = urllib.parse.urlencode(params)
    signature = hmac.new(
        api_secret.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()
    return query + "&signature=" + signature

print("🧨 Cancelling ALL conditional orders (NORMAL + ALGO)...")

# =====================================================
# 1️⃣ CANCEL NORMAL STOP / TP ORDERS
# =====================================================
try:
    orders = client.futures_get_open_orders(symbol=SYMBOL)
except (ConnectionError, ReadTimeout) as e:
    print("🚫 FAILED TO FETCH NORMAL ORDERS:", e)
    orders = []

for o in orders:
    if o["type"] in STOP_TYPES:
        try:
            client.futures_cancel_order(
                symbol=SYMBOL,
                orderId=o["orderId"]
            )
            print(f"❌ Normal cancelled | {o['type']} | ID {o['orderId']}")
            time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ Normal cancel failed | {o['orderId']} | {e}")

# =====================================================
# 2️⃣ CANCEL ALGO / CONDITIONAL ORDERS
# =====================================================
params = {"timestamp": int(time.time() * 1000)}
url = BASE_URL + "/fapi/v1/openAlgoOrders?" + sign(params)

try:
    algo_orders = requests.get(url, headers=headers).json()
except Exception as e:
    print("🚫 FAILED TO FETCH ALGO ORDERS:", e)
    algo_orders = []

for o in algo_orders:
    cancel_params = {
        "symbol": o["symbol"],
        "algoId": o["algoId"],
        "timestamp": int(time.time() * 1000)
    }
    cancel_url = BASE_URL + "/fapi/v1/algoOrder?" + sign(cancel_params)

    try:
        requests.delete(cancel_url, headers=headers)
        print(f"❌ Algo cancelled | algoId {o['algoId']} | trigger {o['triggerPrice']}")
        time.sleep(0.1)
    except Exception as e:
        print(f"⚠️ Algo cancel failed | {o['algoId']} | {e}")

# =====================================================
# 3️⃣ FINAL CONFIRM
# =====================================================
time.sleep(3)

remaining_normal = client.futures_get_open_orders(symbol=SYMBOL)
params = {"timestamp": int(time.time() * 1000)}
remaining_algo = requests.get(
    BASE_URL + "/fapi/v1/openAlgoOrders?" + sign(params),
    headers=headers
).json()

print("\n📡 FINAL CHECK")
print(f"📊 Normal open orders: {len(remaining_normal)}")
print(f"📊 Algo open orders: {len(remaining_algo)}")

if not remaining_normal and not remaining_algo:
    print("✅ ALL CONDITIONAL ORDERS CLEARED")
else:
    print("🚨 SOME ORDERS STILL EXIST")
