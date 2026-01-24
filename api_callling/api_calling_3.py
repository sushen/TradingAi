import os
import sys
import time
from pprint import pprint

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playsound import playsound
from binance.client import Client
from binance.exceptions import BinanceAPIException

from ip_address.ip_address import BinanceAPI, white_ip_list


class APICall:
    def __init__(self):
        self.api_key = os.environ.get("binance_api_key")
        self.api_secret = os.environ.get("binance_api_secret")

        if not self.api_key or not self.api_secret:
            raise ValueError("❌ Binance API keys are missing. Set them in environment variables.")

        self.client = self._initialize_client()

    def _initialize_client(self):
        """
        Hardened Binance Client initialization.
        Handles:
        - ConnectionResetError (10054)
        - Network hiccups
        - Binance congestion
        """
        delay = 5  # start small, grow with failures

        while True:
            try:
                print("🔌 Connecting to Binance API...")

                client = Client(
                    self.api_key,
                    self.api_secret,
                    requests_params={"timeout": 30}
                )

                # Soft warm-up (prevents Windows TCP reset)
                time.sleep(2)

                print("✅ Binance client initialized successfully")
                return client

            except ConnectionResetError:
                print("\n⚠️ Connection reset by remote host (10054)")
                print(f"🔁 Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * 2, 60)

            except Exception as e:
                print(f"\n❌ Error initializing Binance Client: {e}")
                print(f"🌐 Network/Binance issue. Retrying in {delay}s...")
                playsound(r"sounds/InternetDown.mp3")
                time.sleep(delay)
                delay = min(delay * 2, 60)

    def get_candlestick_data(self, symbol="BTCUSDT", interval="1m", limit=5):
        """Fetch candlestick (Kline) data safely."""
        try:
            return self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )

        except ConnectionResetError:
            print("⚠️ Connection reset during candlestick fetch. Reinitializing client...")
            self.client = self._initialize_client()
            return None

        except BinanceAPIException as e:
            print(f"\n❌ Binance API Error (Candlestick Data): {e}")
            return None

        except Exception as e:
            print(f"\n❌ Unexpected Error (Candlestick Data): {e}")
            return None

    def get_futures_balance(self):
        """Fetch futures account balance safely."""
        try:
            balance_info = self.client.futures_account()
            pprint(balance_info)
            return balance_info

        except ConnectionResetError:
            print("⚠️ Connection reset during balance fetch. Reinitializing client...")
            self.client = self._initialize_client()
            return None

        except BinanceAPIException as e:
            print(f"\n❌ Binance API Error (Account Balance): {e}")
            return None

        except Exception as e:
            print(f"\n❌ Unexpected Error (Account Balance): {e}")
            return None


if __name__ == "__main__":

    api = APICall()

    # Check if the public IP is whitelisted
    binance_api = BinanceAPI()
    public_ip = binance_api.get_public_ip()

    if public_ip in white_ip_list:
        print("\n✅ Your IP is whitelisted. Proceeding with API calls...")

        print("\n🔹 Retrieving Recent Candlestick Data...")
        candlestick_data = api.get_candlestick_data(
            symbol="BTCUSDT",
            interval="1m",
            limit=5
        )

        if candlestick_data:
            pprint(candlestick_data)

    else:
        print("\n❌ Your IP is NOT whitelisted. Please add it to the whitelist.")
