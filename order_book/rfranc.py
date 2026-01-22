import requests
import hmac
import hashlib
import time
import urllib.parse
import os

api_key = os.environ.get('binance_api_key')
secret_key= os.environ.get('binance_api_secret')
base_url = "https://fapi.binance.com"
path = "/fapi/v1/openAlgoOrders"
timestamp = round(time.time()*1000)
params = {
    "timestamp": timestamp
}
querystring = urllib.parse.urlencode(params)
signature = hmac.new(secret_key.encode("utf-8"),msg = querystring.encode("utf-8"), digestmod = hashlib.sha256).hexdigest()
url = base_url + path + "?" + querystring + "&signature="+ signature
print(url)
payload = {}
headers= {
    "Content-Type": "application/json",
    "X-MBX-APIKEY": api_key
}
response = requests.request("GET", url, headers=headers, data = payload)
result = response.json()
print("response http status: ", response.status_code)
print("response body: ", result)