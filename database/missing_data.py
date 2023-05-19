import sqlite3
import time
import numpy as np
import pandas as pd
import binance
from database.future_dataframe import GetFutureDataframe
from exchange_info import BinanceExchange
from store_in_db import StoreData
from datetime import datetime
from resample import ResampleData
import warnings

warnings.filterwarnings("ignore")


class MissingDataCollection:
    def __init__(self):
        self.StartTime = time.time()
        print("This Script Start " + time.ctime())

    def get_old_db_data(self, symbol, connection, symbol_id, t=1, limit=250):
        query = '''SELECT subquery.*
                    FROM (
                    SELECT asset_{t}m.*
                    FROM asset_{t}m
                    JOIN symbols ON asset_{t}m.symbol_id = symbols.id
                    WHERE symbols.id = ?
                    ORDER BY asset_{t}m.id DESC
                    LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC'''.format(t=t, limit=limit)
        extra_data = pd.read_sql_query(query, connection, params=(symbol_id,))
        extra_data = extra_data.drop(['id', 'symbol_id'], axis=1)
        extra_data = extra_data.set_index('Time')
        change = extra_data.pop("Change")
        extra_data.insert(9, 'Change', change)
        extra_data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
        query = '''
            SELECT asset_{t}m.id
            FROM asset_{t}m
            ORDER BY asset_{t}m.id DESC
            LIMIT 1
        '''.format(t=t)
        last_db_id = pd.read_sql_query(query, connection)
        last_db_id = last_db_id.iloc[0]['id']
        return last_db_id, extra_data

    def get_new_db_data(self, symbol, connection, symbol_id, start_time):
        query = """
        SELECT asset_1m.*, symbols.symbolName as symbol
        FROM asset_1m
        JOIN symbols ON asset_1m.symbol_id = symbols.id
        WHERE symbols.id = ? AND asset_1m.Time >= datetime(?, 'utc')
        """
        data = pd.read_sql_query(query, connection, params=(symbol_id, start_time))
        data = data.drop(['id', 'symbol_id'], axis=1)
        data = data.set_index('Time')
        data.index = pd.to_datetime(data.index)
        change = data.pop("Change")
        data.insert(9, 'Change', change)
        data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
        return data

    def get_new_data(self, symbol, start_time, end_time):
        try:
            data = GetFutureDataframe().get_range_data(symbol, 1, start_time, end_time)
        except binance.exceptions.BinanceAPIException as e:
            print(f"Binance API exception: {e}")
            return
        print(data)

        if data is None:
            print("Can not find any data for ", symbol)
            return
        return data

    def store_data_in_db(self, store_data, symbol_id, asset_id):
        print("Storing data in asset table")
        store_data.store_asset(symbol_id)
        print("Storing data in cryptoCandle table")
        asset_id = store_data.store_cryptoCandle(symbol_id, asset_id)
        print("Storing data in rsi table")
        store_data.store_rsi(symbol_id, asset_id)
        print("Storing data in movingAverage table")
        store_data.store_movingAverage(symbol_id, asset_id)
        print("Storing data in macd table")
        store_data.store_macd(symbol_id, asset_id)
        print("Storing data in bollinger band table")
        store_data.store_bollingerBand(symbol_id, asset_id)
        print("Storing data in super trend table")
        store_data.store_superTrend(symbol_id, asset_id)

    def grab_missing_1m(self, symbol):
        print("#################################")
        print("Working on 1m")
        connection = sqlite3.connect("big_crypto.db")
        cur = connection.cursor()
        cur.execute("SELECT id FROM symbols WHERE symbolName = ?", (symbol,))
        result = cur.fetchone()
        symbol_id = result[0] if result else None

        # Gate Old data
        extra = 250
        last_db_id, extra_data = self.get_old_db_data(symbol, connection, symbol_id, 1, extra)
        start_time = datetime.strptime(extra_data.index[-1], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.now()

        # Get New data
        data = self.get_new_data(symbol, start_time, end_time)
        print(data)

        store_data = StoreData(data, connection, cur, symbol, 1, extra, extra_data)
        asset_id = np.arange(last_db_id + 1, last_db_id + len(data) + 1)
        self.store_data_in_db(store_data, symbol_id, asset_id)

        connection.commit()
        cur.close()

    def grab_missing_resample(self, symbol):
        print("#################################")
        print("Working on resample")
        connection = sqlite3.connect("big_crypto.db")
        cur = connection.cursor()
        cur.execute("SELECT id FROM symbols WHERE symbolName = ?", (symbol,))
        result = cur.fetchone()
        symbol_id = result[0] if result else None

        rt = [3, 5, 15, 30]
        extra = 250

        for t in rt:
            print(f"Working on {t}m")
            last_db_id, extra_data = self.get_old_db_data(symbol, connection, symbol_id, t, extra)
            start_time = str(extra_data.index[-1])

            data = self.get_new_db_data(symbol, connection, symbol_id, start_time)
            # Resampling
            data = data.rename_axis('Time_index')
            data['Time'] = data.index
            rd = ResampleData(symbol)
            data = rd.resample_to_minute(data, t)
            data.set_index('Time', inplace=True)
            # print(data)
            if len(data) <= t:
                print("Skip for low data")
                continue
            store_data = StoreData(data, connection, cur, symbol, t, extra, extra_data)
            asset_id = np.arange(last_db_id + 1, last_db_id + len(data) + 1)
            self.store_data_in_db(store_data, symbol_id, asset_id)

        connection.commit()
        cur.close()

    def collect_missing_data(self):
        p_symbols = BinanceExchange()
        all_symbols_payers = p_symbols.get_specific_symbols()
        print("All symbols: ", len(all_symbols_payers))

        for i, symbol in enumerate(all_symbols_payers):

            # Grab Missing data
            print(i, symbol)
            self.grab_missing_1m(symbol)
            self.grab_missing_resample(symbol)

            EndTime = time.time()
            print("\nThis Script End " + time.ctime())
            totalRunningTime = EndTime - self.StartTime
            print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")


if __name__ == "__main__":
    data_collection = MissingDataCollection()
    while True:
        data_collection.collect_missing_data()