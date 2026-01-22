# cancel_orders.py

import time
import requests
import hmac
import hashlib
import urllib.parse
from api_callling.api_calling import APICall
from requests.exceptions import ConnectionError, ReadTimeout


class ConditionalOrderCanceller:
    """
    Cancels ALL Futures conditional orders:
    - Normal STOP / TP
    - ALGO / CONDITIONAL (STOP_MARKET, Position SL)
    """

    BASE_URL = "https://fapi.binance.com"

    STOP_TYPES = (
        "STOP_MARKET",
        "TAKE_PROFIT_MARKET",
        "STOP",
        "TAKE_PROFIT"
    )

    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol

        api = APICall()
        self.client = api.client
        self.api_key = api.api_key
        self.api_secret = api.api_secret

        self.headers = {"X-MBX-APIKEY": self.api_key}

    # ---------- helpers ----------

    def _sign(self, params: dict) -> str:
        query = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()
        return query + "&signature=" + signature

    # ---------- normal orders ----------

    def cancel_normal_stops(self):
        try:
            orders = self.client.futures_get_open_orders(symbol=self.symbol)
        except (ConnectionError, ReadTimeout):
            return

        for o in orders:
            if o["type"] in self.STOP_TYPES:
                try:
                    self.client.futures_cancel_order(
                        symbol=self.symbol,
                        orderId=o["orderId"]
                    )
                except Exception:
                    pass

    # ---------- algo orders ----------

    def cancel_algo_stops(self):
        params = {"timestamp": int(time.time() * 1000)}
        url = self.BASE_URL + "/fapi/v1/openAlgoOrders?" + self._sign(params)

        try:
            algo_orders = requests.get(url, headers=self.headers).json()
        except Exception:
            return

        for o in algo_orders:
            cancel_params = {
                "symbol": o["symbol"],
                "algoId": o["algoId"],
                "timestamp": int(time.time() * 1000)
            }
            cancel_url = self.BASE_URL + "/fapi/v1/algoOrder?" + self._sign(cancel_params)
            try:
                requests.delete(cancel_url, headers=self.headers)
            except Exception:
                pass

    # ---------- public API ----------

    def cancel_all(self):
        """Hard reset: clears EVERYTHING that can auto-close a position."""
        self.cancel_normal_stops()
        self.cancel_algo_stops()
