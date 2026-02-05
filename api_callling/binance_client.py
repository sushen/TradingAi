# api_callling/binance_client.py

from binance.client import Client
import time
import os
from playsound import playsound

from resource_path import resource_path

_client = None

def get_binance_client(api_key, api_secret):
    global _client

    if _client is None:
        delay = 5
        while True:
            try:
                print("🔌 Connecting to Binance API (singleton)...")

                client = Client(
                    api_key,
                    api_secret,
                    requests_params={"timeout": 30}
                )

                # 🔥 SOFT handshake (SPOT endpoint, very stable)
                client.get_server_time()

                time.sleep(1)
                _client = client

                print("✅ Binance client initialized (singleton)")
                break

            except Exception as e:
                print(f"❌ Binance init failed: {e}")
                playsound(
                    resource_path(
                        os.path.join("sounds", "Binance_init_failed.mp3")
                    )
                )
                print(f"🔁 Retrying in {delay}s...")
                time.sleep(delay)
                delay = min(delay * 2, 60)

    return _client
