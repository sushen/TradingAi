import os
from binance.client import Client


class BinanceExchange:
    def __init__(self, api_key=os.environ.get('binance_api_key'), api_secret=os.environ.get('binance_api_secret')):
        self.client = Client(api_key, api_secret)

    def get_specific_symbols(self):
        try:
            # Fetch all trading pairs (symbols) from Binance
            trading_pairs = self.client.get_all_tickers()
            # Extract symbol names into a list
            return [ticker['symbol'] for ticker in trading_pairs]
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return []


if __name__ == '__main__':
    binance_exchange = BinanceExchange()
    symbols = binance_exchange.get_specific_symbols()
    print("Fetched Trading Symbols:", symbols)