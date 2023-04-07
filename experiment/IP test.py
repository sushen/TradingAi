import requests

url = "https://api.binance.com/api/v3/time"
# url = "https://checkip.amazonaws.com/"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)