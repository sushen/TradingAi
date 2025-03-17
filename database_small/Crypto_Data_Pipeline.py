import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('C:\\Users\\user\\PycharmProjects\\TradingAiVersion4\\api_callling\\api_calling.py')

import sqlite3
import pandas as pd
import time
import pickle
# from api_calling.api_calling import APICall
from database.future_dataframe import GetFutureDataframe
from exchange.exchange_info import BinanceExchange
from database.store_in_db import StoreData
from create_resample_data import Resample
import warnings

warnings.filterwarnings("ignore")


# ---- DATABASE SETUP ----
def create_database():
    connection = sqlite3.connect('small_crypto.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    tables = {
        "symbols": """
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbolName TEXT UNIQUE
            )
        """,
        "asset": """
            CREATE TABLE IF NOT EXISTS asset (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id INTEGER,
                Open REAL, High REAL, Low REAL, Close REAL,
                Volume REAL, Change REAL, CloseTime INTEGER,
                Trades INTEGER, BuyQuoteVolume REAL, Time TEXT,
                FOREIGN KEY(symbol_id) REFERENCES symbols(id)
            )
        """,
        "cryptoCandle": """
            CREATE TABLE IF NOT EXISTS cryptoCandle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id INTEGER, asset_id INTEGER,
                CDL2CROWS INTEGER, CDL3BLACKCROWS INTEGER, CDL3INSIDE INTEGER,
                CDLENGULFING INTEGER, CDLHARAMI INTEGER, CDLSHOOTINGSTAR INTEGER,
                FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                FOREIGN KEY(asset_id) REFERENCES asset(id)
            )
        """,
    }

    for name, query in tables.items():
        cursor.execute(query)

    connection.commit()
    connection.close()
    print("[INFO] Database setup completed.")


# ---- DATA COLLECTION ----
class DataCollection:
    def __init__(self):
        self.months = 1
        self.days = 30 * self.months
        self.hours = 24 * self.days
        self.minute = self.hours * 60
        print(f"Collecting '{self.minute}' candles")
        self.time_of_data = int(self.minute)
        self.start_time = time.time()
        print("[INFO] Data collection started at:", time.ctime())

    def collect_data(self):
        # api_instance = APICall()
        symbols_list = BinanceExchange().get_specific_symbols(contractType="PERPETUAL", quoteAsset='USDT')

        try:
            with open('symbol_data_already_collected.pkl', 'rb') as f:
                collected_symbols = pickle.load(f)
        except FileNotFoundError:
            collected_symbols = []

        for i, symbol in enumerate(symbols_list):
            if symbol in collected_symbols:
                continue

            try:
                data = GetFutureDataframe().get_minute_data(symbol, 1, self.time_of_data)
                if data is None:
                    continue

                connection = sqlite3.connect('small_crypto.db')
                cursor = connection.cursor()
                store_data = StoreData(data, connection, cursor, symbol)
                symbol_id = store_data.store_symbol()
                store_data.store_asset(symbol_id)
                store_data.store_cryptoCandle(symbol_id)
                store_data.store_rsi(symbol_id)
                store_data.store_movingAverage(symbol_id)
                store_data.store_macd(symbol_id)
                store_data.store_bollingerBand(symbol_id)
                store_data.store_superTrend(symbol_id)

                resample = Resample(data)
                resample.create_minute_data(symbol_id, symbol)

                collected_symbols.append(symbol)
                with open('symbol_data_already_collected.pkl', 'wb') as f:
                    pickle.dump(collected_symbols, f)

                connection.commit()
                cursor.close()
                connection.close()

            except Exception as e:
                print(f"[ERROR] Failed to process {symbol}: {e}")

        print("[INFO] Data collection completed.")


# ---- RESAMPLING ----
class ResampleData:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol
        self.aggregation = {
            "Open": "first", "High": "max", "Low": "min", "Close": "last",
            "Volume": "sum", "Change": "last", "CloseTime": "last",
            "Trades": "sum", "BuyQuoteVolume": "sum", "Time": "first"
        }

    def resample_data(self, df, time):
        df.index = pd.to_datetime(df.index)
        agg_filtered = {key: func for key, func in self.aggregation.items() if key in df}
        if not agg_filtered:
            raise ValueError("No matching columns in DataFrame for resampling.")
        return df.resample(f"{time}T").agg(agg_filtered)


if __name__ == "__main__":
    create_database()
    data_collector = DataCollection()
    data_collector.collect_data()
