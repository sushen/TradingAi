import requests
r = requests.get("https://api.binance.com/api/v3/time", timeout=10)
print(r.status_code, r.headers.get("Content-Type"), len(r.content), r.text[:200])
