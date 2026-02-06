import os
import os
import sys
import time
import json
import threading
import logging
import hmac
import hashlib
import urllib.parse
import ipaddress
import re
from typing import Dict

import requests

try:
    from binance.client import Client as BinanceClient
except Exception:
    BinanceClient = None

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

DEFAULT_IP_SERVICES = [
    "https://api.ipify.org?format=json",
    "https://api64.ipify.org?format=json",
    "https://ipv4.icanhazip.com",
    "https://ipv6.icanhazip.com",
    "https://checkip.amazonaws.com",
]

DEFAULT_CACHE_FILE = os.path.join(os.path.dirname(__file__), "ip_cache.json")
DEFAULT_LOG_FILE = os.path.join(os.path.dirname(__file__), "ip_changes.log")
DEFAULT_API_BASE_URLS = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
]
DEFAULT_FUTURES_BASE_URLS = [
    "https://fapi.binance.com",
    "https://fapi1.binance.com",
    "https://fapi2.binance.com",
    "https://fapi3.binance.com",
]
DEFAULT_TIME_SYNC_INTERVAL_SECONDS = 60
DEFAULT_MANUAL_WHITELIST_FILE = os.path.join(
    os.path.dirname(__file__),
    "manual_whitelist.txt",
)
DEFAULT_MANUAL_WHITELIST_ENV = "BINANCE_MANUAL_WHITELIST"
DEFAULT_MANUAL_WHITELIST_CACHE_TTL_SECONDS = 60
DEFAULT_BEEP_DURATION_SECONDS = 600
DEFAULT_BEEP_INTERVAL_SECONDS = 4.0

_IP_SPLIT_RE = re.compile(r"[,\s]+")


def _parse_url_env(env_name, fallback):
    raw = os.environ.get(env_name)
    if not raw:
        return list(fallback)
    urls = [item.strip() for item in raw.split(",") if item.strip()]
    return urls or list(fallback)


def _parse_ip_tokens(raw):
    if raw is None:
        return set()
    tokens = []
    if isinstance(raw, (list, tuple, set)):
        for item in raw:
            if item is None:
                continue
            tokens.extend(_IP_SPLIT_RE.split(str(item)))
    else:
        tokens = _IP_SPLIT_RE.split(str(raw))

    ips = set()
    for token in tokens:
        token = token.strip().lstrip("\ufeff").strip("\"'").strip()
        if not token:
            continue
        try:
            ip_obj = ipaddress.ip_address(token)
            ips.add(str(ip_obj))
        except ValueError:
            print(f"Invalid IP in manual whitelist ignored: {token}")
    return ips


def _load_manual_whitelist(env_name, file_path):
    manual_ips = set()
    env_raw = os.environ.get(env_name)
    if env_raw:
        manual_ips.update(_parse_ip_tokens(env_raw))

    if file_path and os.path.isfile(file_path):
        try:
            # Use utf-8-sig to safely handle BOM from Windows editors.
            with open(file_path, "r", encoding="utf-8-sig") as f:
                file_raw = f.read()
            manual_ips.update(_parse_ip_tokens(file_raw))
        except OSError as exc:
            print(f"Failed to read manual whitelist file: {exc}")

    return manual_ips


class PublicIPResolver:
    """Fetch public IPv4/IPv6 using multiple external services."""

    def __init__(self, services=None, timeout=5):
        self.services = services or DEFAULT_IP_SERVICES
        self.timeout = timeout

    def _fetch_ip(self, url):
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                ip_text = response.json().get("ip", "").strip()
            else:
                ip_text = response.text.strip()
            if not ip_text:
                return None
            return ipaddress.ip_address(ip_text)
        except (requests.RequestException, ValueError):
            return None

    def fetch(self):
        ips = {}
        for url in self.services:
            ip_obj = self._fetch_ip(url)
            if not ip_obj:
                continue
            if ip_obj.version == 4 and "ipv4" not in ips:
                ips["ipv4"] = str(ip_obj)
            elif ip_obj.version == 6 and "ipv6" not in ips:
                ips["ipv6"] = str(ip_obj)
            if "ipv4" in ips and "ipv6" in ips:
                break
        return ips


class BinanceAPI:
    """Signed Binance API client (SAPI + Futures)."""

    def __init__(
        self,
        api_key=None,
        secret_key=None,
        timeout=10,
        trust_env=None,
        api_base_urls=None,
        futures_base_urls=None,
        time_sync_interval_seconds=DEFAULT_TIME_SYNC_INTERVAL_SECONDS,
    ):
        self.api_key = (
            api_key
            or os.environ.get("binance_api_key")
            or os.environ.get("BINANCE_API_KEY")
        )
        self.secret_key = (
            secret_key
            or os.environ.get("binance_api_secret")
            or os.environ.get("BINANCE_API_SECRET")
        )

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials in environment variables.")

        self.api_base_urls = api_base_urls or _parse_url_env(
            "BINANCE_API_BASE_URLS", DEFAULT_API_BASE_URLS
        )
        self.futures_base_urls = futures_base_urls or _parse_url_env(
            "BINANCE_FUTURES_BASE_URLS", DEFAULT_FUTURES_BASE_URLS
        )
        self.api_base_url = self.api_base_urls[0]
        self.futures_base_url = self.futures_base_urls[0]
        self.timeout = timeout
        self.time_sync_interval_seconds = max(10, int(time_sync_interval_seconds))
        self._time_offset_ms = 0
        self._time_offset_last_sync = 0.0

        self.client = None
        self._client_sapi_error_printed = False
        if BinanceClient is not None:
            try:
                self.client = BinanceClient(
                    self.api_key,
                    self.secret_key,
                    requests_params={"timeout": self.timeout},
                )
                # Soft handshake to sync time offsets in the client.
                try:
                    self.client.get_server_time()
                except Exception:
                    pass
            except Exception as exc:
                print(f"Binance client init failed: {exc}")
                self.client = None

        self.session = requests.Session()
        if trust_env is None:
            trust_env = os.environ.get("BINANCE_TRUST_ENV", "0").lower() in (
                "1",
                "true",
                "yes",
            )
        self.session.trust_env = bool(trust_env)
        self.session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "TradingAi/1.0 (+https://api.binance.com)",
                "X-MBX-APIKEY": self.api_key,
            }
        )

    def _sign(self, params):
        querystring = urllib.parse.urlencode(params, doseq=True)
        return hmac.new(
            self.secret_key.encode("utf-8"),
            msg=querystring.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def _client_sapi_request(self, path):
        if not self.client:
            return None

        request_api = getattr(self.client, "_request_api", None)
        if request_api:
            try:
                return request_api(
                    "get",
                    path,
                    signed=True,
                    version="sapi",
                    data={},
                )
            except Exception as exc:
                msg = str(exc)
                if "Invalid JSON error message from Binance" in msg:
                    if not self._client_sapi_error_printed:
                        print(
                            "⚠️ Binance client SAPI returned an empty response; "
                            "falling back to direct request."
                        )
                        self._client_sapi_error_printed = True
                    return None
                print(f"Binance client SAPI request failed: {exc}")
                return None

        request = getattr(self.client, "_request", None)
        if request:
            try:
                return request("get", path, signed=True, version="sapi", data={})
            except TypeError:
                try:
                    return request("get", path, signed=True, data={})
                except Exception as exc:
                    msg = str(exc)
                    if "Invalid JSON error message from Binance" in msg:
                        if not self._client_sapi_error_printed:
                            print(
                                "⚠️ Binance client SAPI returned an empty response; "
                                "falling back to direct request."
                            )
                            self._client_sapi_error_printed = True
                        return None
                    print(f"Binance client request failed: {exc}")
                    return None
            except Exception as exc:
                msg = str(exc)
                if "Invalid JSON error message from Binance" in msg:
                    if not self._client_sapi_error_printed:
                        print(
                            "⚠️ Binance client SAPI returned an empty response; "
                            "falling back to direct request."
                        )
                        self._client_sapi_error_printed = True
                    return None
                print(f"Binance client request failed: {exc}")
                return None

        return None

    def _ensure_time_sync(self, base_url):
        now = time.time()
        if now - self._time_offset_last_sync < self.time_sync_interval_seconds:
            return
        try:
            response = self.session.get(
                f"{base_url}/api/v3/time", timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            server_time = int(data.get("serverTime"))
            local_time = int(now * 1000)
            self._time_offset_ms = server_time - local_time
            self._time_offset_last_sync = now
        except Exception as exc:
            print(f"Binance time sync failed: {exc}")

    def _signed_request_single(self, method, base_url, endpoint, params=None):
        self._ensure_time_sync(base_url)
        params = dict(params or {})
        params["timestamp"] = int(time.time() * 1000) + self._time_offset_ms
        params.setdefault("recvWindow", 5000)
        params["signature"] = self._sign(params)

        url = f"{base_url}{endpoint}"
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                timeout=self.timeout,
            )
            status = response.status_code
            content_type = response.headers.get("Content-Type", "")
            content_encoding = response.headers.get("Content-Encoding", "")
            content_length = response.headers.get("Content-Length", "")
            text_preview = response.text.strip().replace("\n", " ")[:200]
            if not text_preview and response.content:
                text_preview = repr(response.content[:200])
            data = None
            try:
                data = response.json()
            except ValueError:
                data = None

            if response.ok and data is not None:
                return data

            if data is not None:
                print(
                    "Binance API error response: "
                    f"HTTP {status} | data={data}"
                )
                return data

            if response.ok:
                print(
                    "Binance returned non-JSON response: "
                    f"HTTP {status} | ct={content_type} | "
                    f"enc={content_encoding} | len={content_length} | "
                    f"{text_preview}"
                )
            else:
                print(
                    "Binance request failed: "
                    f"HTTP {status} | ct={content_type} | "
                    f"enc={content_encoding} | len={content_length} | "
                    f"{text_preview}"
                )
            return None
        except requests.RequestException as exc:
            print(f"Binance request failed: {exc}")
            return None

    def _signed_request(self, method, base_urls, endpoint, params=None):
        urls = base_urls if isinstance(base_urls, (list, tuple)) else [base_urls]
        for base_url in urls:
            data = self._signed_request_single(
                method, base_url, endpoint, params=params
            )
            if data is not None:
                return data
        return {}

    def get_api_key_permissions(self):
        """Fetch Binance API key permissions, including whitelisted IPs."""
        if self.client is not None:
            data = self._client_sapi_request("account/apiRestrictions")
            if data is not None:
                return data
            for method_name in ("get_api_key_permission", "get_api_key_permissions"):
                method = getattr(self.client, method_name, None)
                if method:
                    try:
                        return method()
                    except Exception as exc:
                        print(f"Binance client apiKeyPermission failed: {exc}")
                        break
        return self._signed_request(
            "GET", self.api_base_urls, "/sapi/v1/account/apiRestrictions"
        )

    def get_api_key_permissions_legacy(self):
        """Legacy endpoint (deprecated) kept for backward compatibility."""
        if self.client is not None:
            data = self._client_sapi_request("asset/apiKeyPermission")
            if data is not None:
                return data
        return self._signed_request(
            "GET", self.api_base_urls, "/sapi/v1/asset/apiKeyPermission"
        )

    def get_whitelisted_ips(self):
        """Return (ip_restrict, set(ip_list), raw_response, error_code, error_msg)."""
        data = self.get_api_key_permissions()
        print(f"🔹 Binance apiRestrictions response: {data}")
        ip_restrict = False
        ip_list = []
        error_code = None
        error_msg = None
        if isinstance(data, dict):
            ip_restrict = bool(data.get("ipRestrict", False))
            ip_list = data.get("ipList") or []
            error_code = data.get("code")
            error_msg = data.get("msg")

        if isinstance(ip_list, str):
            ip_list = [item.strip() for item in ip_list.split(",") if item.strip()]
        elif isinstance(ip_list, list):
            ip_list = [str(item).strip() for item in ip_list if str(item).strip()]
        else:
            ip_list = []

        return ip_restrict, set(ip_list), data, error_code, error_msg

    def get_account_info(self):
        """Fetch Binance Futures account information."""
        return self._signed_request(
            "GET", self.futures_base_urls, "/fapi/v2/account"
        )

    def get_public_ip(self):
        """Fetch the current public IP address (IPv4 preferred)."""
        ips = PublicIPResolver().fetch()
        return ips.get("ipv4") or ips.get("ipv6") or "Unknown IP"


class IPCache:
    """Local cache of known IPs and last IP."""

    def __init__(self, path):
        self.path = path
        self.known_ips = set()
        self.last_ip = None
        self.last_change_ts = None
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        if not os.path.isfile(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.known_ips = set(data.get("known_ips", []))
            self.last_ip = data.get("last_ip")
            self.last_change_ts = data.get("last_change_ts")
        except (OSError, ValueError):
            self.known_ips = set()
            self.last_ip = None
            self.last_change_ts = None

    def save(self):
        with self._lock:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            data = {
                "known_ips": sorted(self.known_ips),
                "last_ip": self.last_ip,
                "last_change_ts": self.last_change_ts,
            }
            tmp_path = f"{self.path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, self.path)


def _build_logger(log_file):
    logger_name = f"ip_monitor:{log_file}"
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


class IPMonitor:
    """Background IP monitor for public IP and Binance whitelist."""

    def __init__(
        self,
        check_interval_seconds=60,
        whitelist_cache_ttl_seconds=300,
        cache_file=DEFAULT_CACHE_FILE,
        log_file=DEFAULT_LOG_FILE,
        prefer_ipv4=True,
        sound_alert=True,
        manual_whitelist_file=DEFAULT_MANUAL_WHITELIST_FILE,
        manual_whitelist_env=DEFAULT_MANUAL_WHITELIST_ENV,
        manual_whitelist_cache_ttl_seconds=DEFAULT_MANUAL_WHITELIST_CACHE_TTL_SECONDS,
        beep_duration_seconds=DEFAULT_BEEP_DURATION_SECONDS,
        beep_interval_seconds=DEFAULT_BEEP_INTERVAL_SECONDS,
        binance_client=None,
        ip_resolver=None,
    ):
        self.check_interval_seconds = max(5, int(check_interval_seconds))
        self.whitelist_cache_ttl_seconds = max(30, int(whitelist_cache_ttl_seconds))
        self.cache = IPCache(cache_file)
        self.logger = _build_logger(log_file)
        self.prefer_ipv4 = prefer_ipv4
        self.sound_alert = sound_alert
        self.manual_whitelist_file = manual_whitelist_file
        self.manual_whitelist_env = manual_whitelist_env
        self.manual_whitelist_cache_ttl_seconds = max(
            10, int(manual_whitelist_cache_ttl_seconds)
        )
        self.beep_duration_seconds = max(1, int(beep_duration_seconds))
        self.beep_interval_seconds = max(0.1, float(beep_interval_seconds))

        self.ip_resolver = ip_resolver or PublicIPResolver()
        self.binance = binance_client
        if self.binance is None:
            try:
                self.binance = BinanceAPI()
            except ValueError as exc:
                self.binance = None
                print(f"Binance API not configured: {exc}")

        self._whitelist_ips = set()
        self._whitelist_active = False
        self._whitelist_last_fetch = 0.0
        self._manual_whitelist = set()
        self._manual_whitelist_last_load = 0.0
        self._last_whitelist_error_code = None
        self._last_whitelist_error_msg = None
        self._last_whitelist_error_printed = None
        self._last_unwhitelisted_ip = None

        self._stop_event = threading.Event()
        self._thread = None

    def _choose_current_ip(self, ips: Dict[str, str]):
        if self.prefer_ipv4 and ips.get("ipv4"):
            return ips["ipv4"]
        if ips.get("ipv6"):
            return ips["ipv6"]
        return ips.get("ipv4")

    def _get_whitelist(self):
        manual_ips = self._get_manual_whitelist()
        if not self.binance:
            return False, set(), False, manual_ips

        now = time.time()
        if now - self._whitelist_last_fetch < self.whitelist_cache_ttl_seconds:
            return (
                self._whitelist_active,
                set(self._whitelist_ips),
                bool(self._whitelist_ips),
                manual_ips,
            )

        try:
            ip_restrict, ips, _, error_code, error_msg = (
                self.binance.get_whitelisted_ips()
            )
            self._whitelist_active = bool(ip_restrict)
            self._whitelist_ips = set(ips)
            self._last_whitelist_error_code = error_code
            self._last_whitelist_error_msg = error_msg
            if error_code is None:
                self._last_whitelist_error_printed = None
            elif error_code != self._last_whitelist_error_printed:
                if error_code == -2015:
                    print(
                        "⚠️ Binance rejected the whitelist request. "
                        "Your IP may not be whitelisted or the API key "
                        "may lack Read permissions."
                    )
                else:
                    print(
                        "⚠️ Binance whitelist error: "
                        f"code={error_code} msg={error_msg}"
                    )
                self._last_whitelist_error_printed = error_code
        except Exception as exc:
            print(f"Failed to fetch Binance whitelist: {exc}")
        finally:
            self._whitelist_last_fetch = now

        return (
            self._whitelist_active,
            set(self._whitelist_ips),
            bool(self._whitelist_ips),
            manual_ips,
        )

    def _get_manual_whitelist(self):
        now = time.time()
        if now - self._manual_whitelist_last_load < self.manual_whitelist_cache_ttl_seconds:
            return set(self._manual_whitelist)

        file_path = os.environ.get(
            "BINANCE_MANUAL_WHITELIST_FILE",
            self.manual_whitelist_file,
        )
        manual_ips = _load_manual_whitelist(self.manual_whitelist_env, file_path)
        self._manual_whitelist = manual_ips
        self._manual_whitelist_last_load = now
        return set(manual_ips)

    def _append_manual_whitelist(self, ip_address_str):
        file_path = os.environ.get(
            "BINANCE_MANUAL_WHITELIST_FILE",
            self.manual_whitelist_file,
        )
        if not file_path:
            return

        current_manual = self._get_manual_whitelist()
        if ip_address_str in current_manual:
            return

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"{ip_address_str}\n")
            current_manual.add(ip_address_str)
            self._manual_whitelist = current_manual
            self._manual_whitelist_last_load = time.time()
            print(f"✅ Added IP to manual whitelist: {ip_address_str}")
        except OSError as exc:
            print(f"Failed to append manual whitelist: {exc}")

    def _play_sound_alert(self):
        if not self.sound_alert:
            return

        def _worker():
            try:
                from sounds.sound_engine import SoundEngine

                end_time = time.time() + self.beep_duration_seconds
                while time.time() < end_time:
                    SoundEngine().beep(repeat=1, delay=0.0)
                    time.sleep(self.beep_interval_seconds)
            except Exception as exc:
                print(f"Sound alert failed: {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    def _handle_change(self, current_ip):
        old_ip = self.cache.last_ip or "Unknown"
        print("⚠️ IP ADDRESS CHANGED")
        self.logger.warning(
            "IP address changed | old_ip=%s | new_ip=%s", old_ip, current_ip
        )
        self._play_sound_alert()

    def _update_cache(self, current_ip, change_detected):
        changed = False
        if current_ip not in self.cache.known_ips:
            self.cache.known_ips.add(current_ip)
            changed = True
        if current_ip != self.cache.last_ip:
            self.cache.last_ip = current_ip
            changed = True
        if change_detected:
            self.cache.last_change_ts = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime()
            )
            changed = True
        if changed:
            self.cache.save()

    def check_once(self):
        ips = self.ip_resolver.fetch()
        current_ip = self._choose_current_ip(ips)
        if not current_ip:
            self.logger.warning("Unable to resolve public IP.")
            return None

        (
            whitelist_active,
            whitelist_ips,
            whitelist_list_available,
            manual_whitelist_ips,
        ) = self._get_whitelist()
        combined_whitelist = set(whitelist_ips) | set(manual_whitelist_ips)
        combined_list_available = bool(combined_whitelist)

        if current_ip not in combined_whitelist:
            print(f"🔹 Current Public IP: {current_ip}")
        in_whitelist = current_ip in combined_whitelist if combined_list_available else False
        if not in_whitelist:
            if self._last_unwhitelisted_ip != current_ip:
                self._last_unwhitelisted_ip = current_ip
                self._play_sound_alert()
        in_local_cache = current_ip in self.cache.known_ips

        change_detected = (not in_local_cache) and (
            (combined_list_available and not in_whitelist)
            or not combined_list_available
        )
        if change_detected:
            self._handle_change(current_ip)
            self._append_manual_whitelist(current_ip)

        self._update_cache(current_ip, change_detected)
        return current_ip

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.check_once()
            except Exception as exc:
                self.logger.exception("IP monitor error: %s", exc)
            self._stop_event.wait(self.check_interval_seconds)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)


def start_ip_monitor(**kwargs):
    """Convenience helper to start the monitor and return the instance."""
    monitor = IPMonitor(**kwargs)
    monitor.start()
    return monitor


# Deprecated: kept for backward compatibility with older imports.
white_ip_list = []


if __name__ == "__main__":
    monitor = IPMonitor(check_interval_seconds=60)
    monitor.start()
    print("IP monitor started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("IP monitor stopped.")
