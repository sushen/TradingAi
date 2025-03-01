import os

from binance.client import Client
from pprint import pprint

# Replace with your Binance API keys
API_KEY = os.environ.get('binance_api_key')
API_SECRET = os.environ.get('binance_api_secret')

# Initialize Binance Client
client = Client(API_KEY, API_SECRET)

try:
    # Fetch candlestick (Kline) data
    candlestick_data = client.futures_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, limit=5)

    # Print the fetched data
    pprint(candlestick_data)

except Exception as e:
    print(f"Error fetching data: {e}")
