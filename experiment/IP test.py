import requests

server_time = "https://api.binance.com/api/v3/time"
ip_query = 'https://checkip.amazonaws.com'

response_1 = requests.request("GET", server_time)
response_2 = requests.request("GET", ip_query)

print(response_1.text,response_2.text)
