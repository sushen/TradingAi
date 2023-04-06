from binance.client import Client
import os

api_key = os.environ.get('binance_api_key')
api_secret = os.environ.get('binance_api_secret')
client = Client(api_key, api_secret)


def get_symbol_info(symbol="BTCUSDT"):
    """
    Returns important information about a given symbol on Binance.
    :param symbol: the symbol name (e.g. BTCUSDT)
    :return: a dictionary containing the symbol's information
    """
    data = client.get_symbol_info(symbol)
    if data:
        return {
            "symbol": data["symbol"],
            "base_asset": data["baseAsset"],
            "quote_asset": data["quoteAsset"],
            "price_precision": data["baseAssetPrecision"],
            "quantity_precision": data["quotePrecision"],
            "min_notional": float(data["filters"][2]["minNotional"])
        }
    else:
        print("Error getting symbol info")
        return None


def get_all_symbols():
    """
    Returns a list of all available symbols on Binance.
    :return: a list of symbol names
    """
    data = client.get_exchange_info()
    if data:
        return [symbol["symbol"] for symbol in data["symbols"]]
    else:
        print("Error getting symbol list")
        return None


print(get_symbol_info(symbol="BTCUSDT"))
