# cancel_orders.py

import os
import sys
import time
import threading
import requests
import hmac
import hashlib
import urllib.parse
import re
import logging
from api_callling.api_calling import APICall
from requests.exceptions import ConnectionError, ReadTimeout

# ---------------- PATH FIX ----------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from binance.exceptions import BinanceAPIException
from sounds.sound_engine import SoundEngine
from ip_address.ip_address import (
    PublicIPResolver,
    _load_manual_whitelist,
    DEFAULT_MANUAL_WHITELIST_FILE,
    DEFAULT_MANUAL_WHITELIST_ENV,
    DEFAULT_MANUAL_WHITELIST_CACHE_TTL_SECONDS,
)

sound = SoundEngine()
IP_LOG_FILE = os.path.join(PROJECT_ROOT, "ip_address", "ip_changes.log")


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
        self._ip_beep_active = False
        self.BEEP_DURATION_SECONDS = 600
        self.BEEP_INTERVAL_SECONDS = 4.0
        self._last_logged_ip = None
        self._logger = self._build_logger()
        self._manual_whitelist = set()
        self._manual_whitelist_last_load = 0.0
        self._manual_whitelist_ttl = DEFAULT_MANUAL_WHITELIST_CACHE_TTL_SECONDS

    # ---------- helpers ----------

    def _sign(self, params: dict) -> str:
        query = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()
        return query + "&signature=" + signature

    def _build_logger(self):
        logger = logging.getLogger("ip_alert_logger")
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        os.makedirs(os.path.dirname(IP_LOG_FILE), exist_ok=True)
        handler = logging.FileHandler(IP_LOG_FILE, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
        return logger

    def _extract_request_ip(self, exc):
        msg = str(exc)
        match = re.search(r"request ip:\s*([0-9a-fA-F\.:]+)", msg)
        if match:
            return match.group(1)
        return None

    def _get_public_ip(self):
        try:
            ips = PublicIPResolver().fetch()
            return ips.get("ipv4") or ips.get("ipv6")
        except Exception:
            return None

    def _get_manual_whitelist(self):
        now = time.time()
        if now - self._manual_whitelist_last_load < self._manual_whitelist_ttl:
            return set(self._manual_whitelist)

        file_path = os.environ.get(
            "BINANCE_MANUAL_WHITELIST_FILE",
            DEFAULT_MANUAL_WHITELIST_FILE,
        )
        manual_ips = _load_manual_whitelist(DEFAULT_MANUAL_WHITELIST_ENV, file_path)
        self._manual_whitelist = manual_ips
        self._manual_whitelist_last_load = now
        return set(manual_ips)

    def _should_beep_for_ip(self, ip_value):
        if not ip_value:
            return True
        return ip_value not in self._get_manual_whitelist()

    def _log_ip_issue(self, message, ip_value):
        if ip_value and ip_value == self._last_logged_ip:
            return
        self._last_logged_ip = ip_value
        ip_display = ip_value or "Unknown"
        print(f"⚠️ {message} | ip={ip_display}")
        self._logger.warning("%s | ip=%s", message, ip_display)

    def _is_ip_whitelist_error(self, exc):
        code = getattr(exc, "code", None)
        if code == -2015:
            return True
        msg = str(exc)
        return (
            "code=-2015" in msg
            or "Invalid API-key, IP, or permissions" in msg
        )

    def _start_ip_beep(self):
        if self._ip_beep_active:
            return
        self._ip_beep_active = True

        def _worker():
            try:
                end_time = time.time() + self.BEEP_DURATION_SECONDS
                while time.time() < end_time:
                    sound.beep(repeat=1, delay=0.0)
                    time.sleep(self.BEEP_INTERVAL_SECONDS)
            finally:
                self._ip_beep_active = False

        threading.Thread(target=_worker, daemon=True).start()

    # ---------- normal orders ----------

    def cancel_normal_stops(self):
        try:
            orders = self.client.futures_get_open_orders(symbol=self.symbol)
        except BinanceAPIException as e:
            if self._is_ip_whitelist_error(e):
                ip_value = self._extract_request_ip(e) or self._get_public_ip()
                self._log_ip_issue(
                    "Binance API rejected request (-2015)",
                    ip_value,
                )
                if self._should_beep_for_ip(ip_value):
                    print("⚠️ IP not whitelisted. Sound alert triggered.")
                    self._start_ip_beep()
            return
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

        if isinstance(algo_orders, dict) and "code" in algo_orders:
            if algo_orders.get("code") == -2015:
                ip_value = self._get_public_ip()
                self._log_ip_issue(
                    "Binance API rejected request (-2015)",
                    ip_value,
                )
                if self._should_beep_for_ip(ip_value):
                    print("⚠️ IP not whitelisted. Sound alert triggered.")
                    self._start_ip_beep()
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
