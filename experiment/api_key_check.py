import os
import requests
import hmac
import hashlib
import time
import urllib.parse


class BinanceAPI:
    def __init__(self):
        self.api_key = os.environ.get('binance_api_key')
        self.secret_key = os.environ.get('binance_api_secret')
        self.spot_url = "https://api.binance.com"  # Spot API for whitelisted IPs
        self.futures_url = "https://fapi.binance.com"  # Futures API for account info

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials in environment variables.")

    def _generate_signature(self, params):
        """Generate HMAC SHA256 signature."""
        querystring = urllib.parse.urlencode(params)
        return hmac.new(self.secret_key.encode('utf-8'), msg=querystring.encode('utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    def _send_request(self, method, endpoint, params=None, use_futures=False):
        """Send a signed request to Binance API."""
        base_url = self.futures_url if use_futures else self.spot_url  # Select correct API
        if params is None:
            params = {}

        params["timestamp"] = round(time.time() * 1000)
        params["signature"] = self._generate_signature(params)

        url = f"{base_url}{endpoint}?{urllib.parse.urlencode(params)}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-MBX-APIKEY': self.api_key
        }

        response = requests.request(method, url, headers=headers)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("❌ Binance API did not return a valid response.")
            return {}

    def get_whitelisted_ips(self):
        """Fetch all whitelisted IPs (Requires Spot API)."""
        response = self._send_request("GET", "/sapi/v1/account/apiRestrictions")
        return response.get("ipRestrict", {}).get("ipList", [])

    def get_account_info(self):
        """Fetch Binance Futures account information (Requires Futures API)."""
        response = self._send_request("GET", "/fapi/v2/account", use_futures=True)
        if "msg" in response:
            print(f"❌ Error fetching account info: {response['msg']}")
        return response

    def get_public_ip(self):
        """Fetch the current public IP address."""
        try:
            response = requests.get("https://api64.ipify.org?format=json")
            return response.json().get("ip", "Unknown IP")
        except requests.RequestException:
            return "Unknown IP"


# **Hardcoded whitelist (in case API call fails)**
white_ip_list = ["103.51.85.49",
                 "103.51.85.60",
                 "103.51.85.38",
                 "103.51.85.61",
                 "103.51.85.41",
                 "103.51.85.62",
                 "103.51.85.57",
                 "103.51.85.39",
                 "103.51.85.47",
                 "103.51.85.52"
                 ]

# Initialize API
binance_api = BinanceAPI()

# Fetch and print public IP
public_ip = binance_api.get_public_ip()
print("\n🔹 Your Public IP Address:", public_ip)

# Fetch whitelisted IPs (Using Spot API)
whitelisted_ips = binance_api.get_whitelisted_ips()

# **Fallback to hardcoded whitelist if API fails**
if not whitelisted_ips:
    print("⚠️ Using hardcoded whitelist (API failed to retrieve data).")
    whitelisted_ips = white_ip_list

print("\n🔹 Whitelisted IPs:")
for ip in whitelisted_ips:
    print(f"   - {ip}")

# Check if IP is whitelisted and fetch account info
if public_ip in whitelisted_ips:
    print("\n✅ Your IP is whitelisted. Fetching account information...")
    account_info = binance_api.get_account_info()
    print("\n🔹 Account Information:", account_info)

    if "msg" in account_info:
        print(f"🔹 Binance sees your request coming from IP: {account_info['msg'].split()[-1]}")

else:
    print("\n❌ Your IP is NOT whitelisted. Please add it to the whitelist.")
