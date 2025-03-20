import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playsound import playsound
import time
from pprint import pprint
from binance.client import Client
from binance.exceptions import BinanceAPIException

from ip_address.ip_address import BinanceAPI, white_ip_list


class APICall:
    def __init__(self):
        self.api_key = os.environ.get('binance_api_key')
        self.api_secret = os.environ.get('binance_api_secret')

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ Binance API keys are missing. Set them in environment variables.")

        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize Binance Client with error handling."""
        try:
            return Client(self.api_key, self.api_secret)
        except Exception as e:
            print(f"\n❌ Error initializing Binance Client: {e}")
            print("Internet Down. See the internet connection.")
            playsound(r'C:\Users\user\PycharmProjects\TradingAiVersion8\sounds\InternetDown.mp3')
            playsound(r'C:\Users\user\PycharmProjects\TradingAiVersion8\sounds\InternetDown.mp3')
            time.sleep(61)  # Wait before retrying
            return Client(self.api_key, self.api_secret)

    def get_candlestick_data(self, symbol="BTCUSDT", interval="1m", limit=5):
        """Fetch candlestick (Kline) data."""
        try:
            return self.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        except BinanceAPIException as e:
            print(f"\n❌ Binance API Error (Candlestick Data): {e}")
            return None

    def get_futures_balance(self):
        """Fetch futures account balance with debugging."""
        try:
            balance_info = self.client.futures_account()
            pprint(balance_info)  # Debugging: Print raw response
            return balance_info
        except BinanceAPIException as e:
            print(f"\n❌ Binance API Error (Account Balance): {e}")
            return None


if __name__ == "__main__":
    api = APICall()

    # Check if the public IP is whitelisted
    binance_api = BinanceAPI()
    public_ip = binance_api.get_public_ip()

    if public_ip in white_ip_list:
        print("\n✅ Your IP is whitelisted. Proceeding with API calls...")

        # Retrieve account balance
        # print("\n🔹 Retrieving Futures Account Balance...")
        # balance_info = api.get_futures_balance()
        # if balance_info:
        #     print(balance_info)

        # Retrieve candlestick data
        print("\n🔹 Retrieving Recent Candlestick Data...")
        candlestick_data = api.get_candlestick_data()
        if candlestick_data:
            print(candlestick_data)

    else:
        print("\n❌ Your IP is NOT whitelisted. Please add it to the whitelist.")
