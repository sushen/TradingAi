import os
import time
import binance
import requests
from binance.client import Client


class BinanceNetwork:
    def __init__(self):
        self.api_key = os.environ.get('binance_api_key')
        self.api_secret = os.environ.get('binance_api_secret')
        self.client = self.connect()

    def connect(self):
        while True:
            try:
                print("Trying to connect...")
                client = Client(self.api_key, self.api_secret)
                server_time = client.get_server_time()
                if server_time:
                    print("Connection to Binance API is working.")
                    return client
            except requests.exceptions.ConnectionError as e:
                print(f"Connection to Binance API failed with error: {e}")
                time.sleep(60)
                continue
            except binance.exceptions.BinanceAPIException as e:
                print(f"Binance API exception: {e}")
                time.sleep(60)
                continue
            except binance.exceptions.BinanceOrderException as e:
                print(f"Binance order exception: {e}")
                time.sleep(60)
                continue
            time.sleep(60)

    def get_server_time(self):
        server_time = self.client.get_server_time()
        return server_time['serverTime']

    def get_time_diff(self):
        server_time = self.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = (server_time - local_time) / 1000
        return time_diff

if __name__ == "__main__":
    bn = BinanceNetwork()
    server_time = bn.get_server_time()
    print("Server time: ", server_time)
    time_diff = bn.get_time_diff()
    print(f"The time difference between server and local machine is {time_diff:.2f} seconds")
