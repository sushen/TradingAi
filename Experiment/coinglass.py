from pprint import pprint

import requests
symbol = "BTC"
interval = "1m"
url = 'https://open-api.coinglass.com/api/pro/v1/futures/funding_rates_chart?symbol=BTC&type=C'
# url = f"http://open-api.coinglass.com/api/pro/v1/futures/openInterest?interval={interval}&symbol={symbol}"
params = {}
headers = {
  'coinglassSecret': '55508be539fc4085bf2ebed07f87f280'
}
response = requests.request("GET", url, headers=headers, data = params)
pprint(response.text.encode('utf8'))
