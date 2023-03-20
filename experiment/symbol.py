from binance.client import Client


client = Client()
client.ping()

print(client.ping())


# info = client.get_symbol_info('BNBBTC')
# print(info)
# print(client.get_ticker())