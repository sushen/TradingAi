import os
import sys
import time
from pprint import pprint

from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import ReadTimeout, ConnectionError
from playsound import playsound

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ip_address.ip_address import BinanceAPI, white_ip_list


class APICall:
    def __init__(self, max_retries=3, retry_delay=10):
        self.api_key = os.environ.get("binance_api_key")
        self.api_secret = os.environ.get("binance_api_secret")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ Binance API keys are missing. Set them in environment variables.")

        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = self._initialize_client()

    # --------------------------------------------------
    # CLIENT INITIALIZATION (SAFE + RETRY)
    # --------------------------------------------------
    def _initialize_client(self):
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"🔌 Initializing Binance client (attempt {attempt})...")
                return Client(self.api_key, self.api_secret)
            except Exception as e:
                print(f"\n❌ Binance Client init failed: {e}")
                print("🌐 Internet down or Binance not responding.")

                try:
                    playsound(r"sounds/InternetDown.mp3")
                except Exception:
                    pass  # sound must never block trading logic

                if attempt < self.max_retries:
                    print(f"⏳ Retrying in {self.retry_delay}s...\n")
                    time.sleep(self.retry_delay)
                else:
                    print("🚨 Max retries reached. Client unavailable.\n")
                    return None

    # --------------------------------------------------
    # SAFE API CALL WRAPPER (AUTO RECOVER)
    # --------------------------------------------------
    def _safe_call(self, func, *args, **kwargs):
        if not self.client:
            print("🔄 Binance client missing. Attempting re-initialization...")
            self.client = self._initialize_client()
            if not self.client:
                print("⚠️ Client still unavailable. Skipping API call.")
                return None

        try:
            return func(*args, **kwargs)

        except (BinanceAPIException, ReadTimeout, ConnectionError) as e:
            print(f"\n⚠️ Binance API / Network error: {e}")
            print("⏭ Skipping this cycle, retrying next loop.")
            return None

        except Exception as e:
            print(f"\n🔥 Unexpected error: {e}")
            return None

    # --------------------------------------------------
    # PUBLIC API METHODS
    # --------------------------------------------------
    def get_candlestick_data(self, symbol="BTCUSDT", interval="1m", limit=5):
        return self._safe_call(
            self.client.futures_klines,
            symbol=symbol,
            interval=interval,
            limit=limit
        )

    def get_futures_balance(self):
        data = self._safe_call(self.client.futures_account)
        if data:
            pprint(data)
        return data


# --------------------------------------------------
# STANDALONE TEST
# --------------------------------------------------
if __name__ == "__main__":
    api = APICall()

    binance_api = BinanceAPI()
    public_ip = binance_api.get_public_ip()

    if public_ip in white_ip_list:
        print("\n✅ Your IP is whitelisted. Proceeding with API calls...")

        print("\n🔹 Retrieving Recent Candlestick Data...")
        candles = api.get_candlestick_data()

        if candles:
            print(candles)
        else:
            print("⚠️ No data received (API skipped this round).")

    else:
        print("\n❌ Your IP is NOT whitelisted. Please add it to the whitelist.")
