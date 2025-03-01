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
        self.base_url = "https://fapi.binance.com"  # Futures API base URL

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials in environment variables.")

    def _generate_signature(self, params):
        """Generate HMAC SHA256 signature."""
        querystring = urllib.parse.urlencode(params)
        return hmac.new(self.secret_key.encode('utf-8'), msg=querystring.encode('utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    def _send_request(self, method, endpoint, params=None):
        """Send a signed request to Binance API."""
        if params is None:
            params = {}

        params["timestamp"] = round(time.time() * 1000)
        params["signature"] = self._generate_signature(params)

        url = f"{self.base_url}{endpoint}?{urllib.parse.urlencode(params)}"
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

    def get_account_info(self):
        """Fetch Binance Futures account information."""
        response = self._send_request("GET", "/fapi/v2/account")

        print("\n🔹 Raw Account Information Response:", response)  # Debugging

        # Check if Binance returns an error with IP info
        if isinstance(response, dict):
            for key, value in response.items():
                if isinstance(value, str) and "request ip:" in value:
                    # print("Its working")
                    print(f"🔹 Binance sees your request coming from IP: {value.split()[-1]}")

        return response

    def get_public_ip(self):
        """Fetch the current public IP address."""
        try:
            response = requests.get("https://api64.ipify.org?format=json")
            return response.json().get("ip", "Unknown IP")
        except requests.RequestException:
            return "Unknown IP"


# Hardcoded whitelist (since API fails to retrieve it)
white_ip_list = ["103.51.85.49", "103.51.85.60", "103.51.85.38",
                 "103.51.85.61", "103.51.85.41", "103.51.85.62",
                 "103.51.85.57","103.51.85.53","103.51.85.35",
                 "103.51.85.39","103.51.85.56", "103.51.85.33",
                 "152.42.242.103"
                 ]

if __name__ == "__main__":
    # Initialize API
    binance_api = BinanceAPI()

    # Fetch and print public IP
    public_ip = binance_api.get_public_ip()
    print("\n🔹 Your Public IP Address:", public_ip)

    # Use hardcoded whitelist
    print("⚠️ Using hardcoded whitelist (API failed to retrieve data).")
    print("\n🔹 Whitelisted IPs:")
    for ip in white_ip_list:
        print(f"   - {ip}")

    # Check if IP is whitelisted and fetch account info
    if public_ip in white_ip_list:
        print("\n✅ Your IP is whitelisted. Fetching account information...")
        account_info = binance_api.get_account_info()
        print("\n🔹 Account Information:", account_info)
    else:
        print("\n❌ Your IP is NOT whitelisted. Please add it to the whitelist.")
