import requests


class BinanceExchange:

    def __init__(self):
        self.url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        self.exchange_info = None
        self.get_exchange_info()

    def get_exchange_info(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.exchange_info = response.json()

    def get_all_contract_types(self):
        contract_types = set(symbol['contractType'] for symbol in self.exchange_info['symbols'])
        return contract_types

    def get_all_symbols(self):
        """
        Returns a list of all available symbols on Binance.
        :return: a list of symbol names
        """
        symbols = [symbol['symbol'] for symbol in self.exchange_info['symbols']]
        return symbols

    def get_specific_symbols(self, contractType="PERPETUAL", quoteAsset='BUSD'):
        """
        Returns all important BUSD symbol on Binance.
        :return: a list containing the symbol's
        """
        result = [symbol['symbol'] for symbol in self.exchange_info['symbols'] if
                  symbol['contractType'] == contractType and symbol['quoteAsset'] == quoteAsset]
        return result

if __name__ == "__main__":
    binance = BinanceExchange()

    # Get all contract types
    contract_types = binance.get_all_contract_types()
    print("All contract currently available: ", f"(Length: {len(contract_types)})", contract_types)

    # Get all symbols
    symbols = binance.get_all_symbols()
    print("All Symbols: ", f"(Length: {len(symbols)})", symbols)

    # Get BUSD symbols that are PERPETUAL BUSD futures
    BUSD_symbols = binance.get_specific_symbols(contractType="PERPETUAL", quoteAsset='BUSD')
    print("PERPETUAL BUSD Symbols: ", f"(Length: {len(BUSD_symbols)})", BUSD_symbols)

    # Get USDT symbols that are PERPETUAL USDT futures
    USDT_symbols = binance.get_specific_symbols(contractType="PERPETUAL", quoteAsset='USDT')
    print("PERPETUAL USDT Symbols: ", f"(Length: {len(USDT_symbols)})", USDT_symbols)

    # Get BTC symbols that are PERPETUAL USDT futures
    # TODO : Make a function for BTC
    BTC_symbols = binance.get_specific_symbols(contractType="PERPETUAL", quoteAsset='BTC')
    print("PERPETUAL BTC Symbols: ", f"(Length: {len(BTC_symbols)})", BTC_symbols)
