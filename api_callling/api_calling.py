import os
import sys
from pprint import pprint

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException
from ip_address.ip_address import BinanceAPI, white_ip_list

from api_callling.binance_client import get_binance_client


class APICall:
    def __init__(self):
        self.api_key = os.environ.get("binance_api_key")
        self.api_secret = os.environ.get("binance_api_secret")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ Binance API keys are missing.")

        # ✅ SINGLE shared client for entire app
        self.client = get_binance_client(self.api_key, self.api_secret)

    def get_candlestick_data(self, symbol="BTCUSDT", interval="1m", limit=5):
        try:
            return self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
        except BinanceAPIException as e:
            print(f"❌ Binance API Error (Candles): {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error (Candles): {e}")
            return None

    def get_futures_balance(self):
        try:
            balance_info = self.client.futures_account()
            pprint(balance_info)
            return balance_info
        except BinanceAPIException as e:
            print(f"❌ Binance API Error (Balance): {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error (Balance): {e}")
            return None
