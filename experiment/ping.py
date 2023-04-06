import os
import time
from binance.client import Client

api_key = os.environ.get('binance_api_key')
api_secret = os.environ.get('binance_api_secret')

while True:
    try:
        print("Trying to connect...")
        client = Client(api_key, api_secret)
        server_time = client.get_server_time()
        if server_time:
            print("Connection to Binance API is working.")
    except Exception as e:
        print(f"Connection to Binance API failed with error: {e}")
        time.sleep(60)
        continue
    time.sleep(60)
