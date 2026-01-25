import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from requests.exceptions import ConnectionError
from api_callling.binance_client import get_binance_client


def safe_futures_klines(
    api_instance,
    symbol,
    interval,
    startTime=None,
    endTime=None,
    limit=1500,
    retries=5
):
    delay = 3

    for attempt in range(retries):
        try:
            return api_instance.client.futures_klines(
                symbol=symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            )

        except (ConnectionResetError, ConnectionError):
            print("⚠️ Futures connection reset. Reconnecting Binance client...")
            time.sleep(delay)

            # 🔁 rebuild singleton client
            api_instance.client = get_binance_client(
                api_instance.api_key,
                api_instance.api_secret
            )

            delay = min(delay * 2, 30)

        except Exception as e:
            print(f"❌ Futures klines error: {e}")
            return None

    print("❌ Futures klines failed after retries")
    return None
