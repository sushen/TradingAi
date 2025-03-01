import os
from pprint import pprint

from binance.client import Client
from binance.exceptions import BinanceAPIException

from api_callling.api_calling import APICall

api_key = os.environ.get('binance_api_key')
api_secret = os.environ.get('binance_api_secret')

client = Client(api_key, api_secret, tld="com")

# Explicitly set the Futures API URL
client.FUTURES_API_URL = "https://fapi.binance.com"

try:
    response = client.futures_exchange_info()
    print("✅ Futures API is working!")
except BinanceAPIException as e:
    print("❌ Binance API Error:", e)
except Exception as e:
    print("❌ General Error:", e)

print("\n🔹 Retrieving Futures Account Balance...")

api = APICall()
try:
    # balance_info = api.client.futures_account()  # Use this instead
    balance_info = client.futures_account()

    pprint(balance_info)
except BinanceAPIException as e:
    print(f"\n❌ Binance API Error: {e}")

