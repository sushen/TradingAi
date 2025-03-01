import sqlite3
import time
import numpy as np
import pandas as pd
import binance
from database.future_dataframe import GetFutureDataframe
from database.exchange_info import BinanceExchange
from database.store_in_db import StoreData
from datetime import datetime, timedelta
from database.resample import ResampleData
import pytz
import warnings

warnings.filterwarnings("ignore")


class MissingDataCollection:
    def __init__(self, database="big_crypto_4years.db"):
        self.StartTime = time.time()
        self.database = database
        print("This Script Start " + time.ctime())

    def get_old_db_data(self, symbol, connection, symbol_id, interval=1, lookback=250):
        query = '''SELECT subquery.*
                    FROM (
                    SELECT asset_{interval}m.*
                    FROM asset_{interval}m
                    JOIN symbols ON asset_{interval}m.symbol_id = symbols.id
                    WHERE symbols.id = ?
                    ORDER BY asset_{interval}m.id DESC
                    LIMIT {lookback}
                    ) AS subquery
                    ORDER BY subquery.id ASC'''.format(interval=interval, lookback=lookback)
        extra_data = pd.read_sql_query(query, connection, params=(symbol_id,))
        extra_data = extra_data.drop(['id', 'symbol_id'], axis=1)
        extra_data = extra_data.set_index('Time')
        change = extra_data.pop("Change")
        extra_data.insert(9, 'Change', change)
        extra_data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
        query = '''
            SELECT asset_{interval}m.id
            FROM asset_{interval}m
            ORDER BY asset_{interval}m.id DESC
            LIMIT 1
        '''.format(interval=interval)
        last_db_id = pd.read_sql_query(query, connection)
        last_db_id = last_db_id.iloc[0]['id']
        return last_db_id, extra_data

    def get_new_db_data(self, symbol, connection, symbol_id, start_time):
        query = """
        SELECT asset_1m.*, symbols.symbolName as symbol
        FROM asset_1m
        JOIN symbols ON asset_1m.symbol_id = symbols.id
        WHERE symbols.id = ? AND asset_1m.Time > ?
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
        connection = sqlite3.connect(self.database)
        cur = connection.cursor()
        cur.execute("SELECT id FROM symbols WHERE symbolName = ?", (symbol,))
        result = cur.fetchone()
        symbol_id = result[0] if result else None

        # Gate Old data
        extra = 250
        last_db_id, extra_data = self.get_old_db_data(symbol, connection, symbol_id, 1, extra)

        # ** Fix: Check if extra_data is empty **
        if extra_data.empty:
            print(f"No historical data found for {symbol}, skipping...")
            cur.close()
            connection.close()
            return  # Skip processing if no data found

        start_time = datetime.strptime(extra_data.index[-1], "%Y-%m-%d %H:%M:%S")
        start_time = start_time.replace(tzinfo=pytz.utc)  # Make start_time offset-aware
        start_time += timedelta(minutes=1)
        end_time = datetime.now(pytz.utc)

        # Get New data
        data = self.get_new_data(symbol, start_time, end_time)
        if data is None or data.empty:
            print("No new data retrieved, skipping...")
            return

        store_data = StoreData(data, connection, cur, symbol, 1, len(extra_data), extra_data)
        asset_id = np.arange(last_db_id + 1, last_db_id + len(data) + 1)
        self.store_data_in_db(store_data, symbol_id, asset_id)

        connection.commit()
        cur.close()

    def grab_missing_resample(self, symbol):
        print("#################################")
        print("Working on resample")
        connection = sqlite3.connect(self.database)
        cur = connection.cursor()
        cur.execute("SELECT id FROM symbols WHERE symbolName = ?", (symbol,))
        result = cur.fetchone()
        symbol_id = result[0] if result else None

        rt = [3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
        extra = 250

        for t in rt:
            print(f"Working on {t}m")
            last_db_id, extra_data = self.get_old_db_data(symbol, connection, symbol_id, t, extra)

            # ** Fix: Check if extra_data is empty **
            if extra_data.empty:
                print(f"No historical data found for {symbol} on {t}m interval, skipping...")
                continue

            start_time = str(extra_data.index[-1])

            data = self.get_new_db_data(symbol, connection, symbol_id, start_time)
            if data.empty:
                continue  # Skip if no data is retrieved

            # Resampling
            data = data.rename_axis('Time_index')
            data['Time'] = data.index
            if len(data) <= t:
                print("Skip for low data")
                continue
            rd = ResampleData(symbol)
            data = rd.resample_to_minute(data, t)
            data.set_index('Time', inplace=True)
            store_data = StoreData(data, connection, cur, symbol, t, len(extra_data), extra_data)
            asset_id = np.arange(last_db_id + 1, last_db_id + len(data) + 1)
            self.store_data_in_db(store_data, symbol_id, asset_id)

        connection.commit()
        cur.close()

    def collect_missing_data_single_symbols(self, symbol):
        # Grab Missing data
        print(symbol)
        self.grab_missing_1m(symbol)
        self.grab_missing_resample(symbol)

        EndTime = time.time()
        print("\nThis Script End " + time.ctime())
        totalRunningTime = EndTime - self.StartTime
        print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")


if __name__ == "__main__":
    data_collection = MissingDataCollection()
    data_collection.collect_missing_data_single_symbols("BTCUSDT")
