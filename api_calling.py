"""
https://python-binance.readthedocs.io/en/latest/overview.html
"""
import os
import time

from binance.client import Client


class APICall:
    try:
        api_key = os.environ.get('binance_api_key')
        api_secret = os.environ.get('binance_api_secret')
        client = Client(api_key, api_secret)

        # api_key = os.environ.get('binance_api_key_testnet')
        # print(api_key)
        # api_secret = os.environ.get('binance_api_secret_testnet')
        # print(api_secret)
        # client = Client(api_key, api_secret, testnet=True)

    except:
        time.sleep(61)
        api_key = os.environ.get('binance_api_key')
        api_secret = os.environ.get('binance_api_secret')
        client = Client(api_key, api_secret)


# lav = APICall().client.futures_change_leverage(symbol="BTCBUSD", leverage=5)
# print(lav)
# ord = APICall().client.futures_create_order(symbol="BTCBUSD", side='BUY', type='MARKET', quantity=0.1)
# print(ord)
