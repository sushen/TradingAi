"""
Script Name: store_in_db.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
from indicator_ai.candle_pattern import MakeCandlePattern
from indicator_ai.rsi import Rsi
from indicator_ai.moving_average_signal import MovingAverage
from indicator_ai.macd import Macd
from indicator_ai.bollinger_bands import BollingerBand
from indicator_ai.super_trend import SuperTrend
import warnings

warnings.filterwarnings("ignore")


class StoreData:
    def __init__(self, data, connection, cur, symbol, interval=1, extra=0, extra_data=None):
        self.data = data
        self.connection = connection
        self.cur = cur
        self.symbol = symbol
        self.interval = interval
        self.extra = extra
        self.extra_data = extra_data

    def store_symbol(self):
        self.cur.execute("INSERT INTO symbols (symbolName) VALUES (?) RETURNING id", (self.symbol,))
        symbol_id = self.cur.fetchone()[0]
        # print(f"symbol_id: {symbol_id}")
        return symbol_id

    def store_asset(self, symbol_id):
        df = self.data.copy()
        # print(df)
        df.drop("symbol", axis=1, inplace=True)  # Drop symbol column
        df.insert(0, 'symbol_id', np.ones(len(df), dtype=np.int16) * symbol_id)
        df.to_sql(f'asset_{self.interval}', self.connection, if_exists='append', index=False)

    def store_cryptoCandle(self, symbol_id, asset_id=None):
        make_pattern = MakeCandlePattern()
        if self.extra_data is not None:
            new_data = pd.concat([self.extra_data, self.data], axis=0)
            pattern = make_pattern.pattern(new_data)
            pattern = pattern.iloc[self.extra:]
        else:
            pattern = make_pattern.pattern(self.data)
        pattern.insert(0, 'symbol_id', np.ones(len(pattern), dtype=np.int16) * symbol_id)
        pattern.insert(0, 'asset_id', asset_id)
        pattern.to_sql(f'cryptoCandle_{self.interval}', self.connection, if_exists='append', index=False)

    def store_rsi(self, symbol_id, asset_id):
        rsi = Rsi()
        rsi_data = rsi.create_rsi(self.data)
        if 'CloseTime' not in rsi_data.columns:
            rsi_data['CloseTime'] = self.data['CloseTime']
        rsi_data['CloseTime'] = pd.to_datetime(rsi_data['CloseTime'], unit='ms')
        rsi_data['CloseTime'] = rsi_data['CloseTime'].view('int64') // 10 ** 9  # Convert to seconds
        rsi_data = rsi_data[['CloseTime', 'signal']]
        rsi_data.insert(0, 'symbol_id', np.ones(len(rsi_data), dtype=np.int16) * symbol_id)
        rsi_data.insert(1, 'asset_id', asset_id)
        rsi_data.to_sql(f'rsi_{self.interval}', self.connection, if_exists='append', index=False)

        # print(rsi_data)
        # print(input("Rsi Data in going to enter in Database:"))

    def store_movingAverage(self, symbol_id, asset_id):
        ma = MovingAverage()
        ma_data = ma.create_moving_average(self.data)
        if 'CloseTime' not in ma_data.columns:
            ma_data['CloseTime'] = self.data['CloseTime']
        ma_data['CloseTime'] = pd.to_datetime(ma_data['CloseTime'], unit='ms')
        ma_data['CloseTime'] = ma_data['CloseTime'].view('int64') // 10 ** 9  # Convert to seconds
        ma_data = ma_data[['long_golden', 'short_medium', 'short_long', 'short_golden', 'medium_long', 'medium_golden','CloseTime']]
        ma_data.insert(0, 'symbol_id', np.ones(len(ma_data), dtype=np.int16) * symbol_id)
        ma_data.insert(1, 'asset_id', asset_id)
        ma_data.to_sql(f'movingAverage_{self.interval}', self.connection, if_exists='append', index=False)

        # print(ma_data)
        # print(input("Moving Average Data in going to enter in Database:"))

    def store_macd(self, symbol_id, asset_id):
        macd = Macd()
        macd_data = macd.create_macd(self.data)

        if 'CloseTime' not in macd_data.columns:
            macd_data['CloseTime'] = self.data['CloseTime']

        macd_data['CloseTime'] = pd.to_datetime(macd_data['CloseTime'], unit='ms')
        macd_data['CloseTime'] = macd_data['CloseTime'].view('int64') // 10 ** 9  # Convert to seconds

        # Make sure CloseTime is included in the final DataFrame before selecting other columns
        macd_data = macd_data[['CloseTime', 'new_signal']]  # Include CloseTime column
        macd_data = macd_data.rename(columns={'new_signal': 'signal'})  # Rename column for clarity

        macd_data.insert(0, 'symbol_id', np.ones(len(macd_data), dtype=np.int16) * symbol_id)
        macd_data.insert(1, 'asset_id', asset_id)

        macd_data.to_sql(f'macd_{self.interval}', self.connection, if_exists='append', index=False)

        # Print macd_data with CloseTime
        # print(macd_data)
        # print(input("MACD Data in going to enter in Database:"))

    def store_bollingerBand(self, symbol_id, asset_id):
        bb = BollingerBand()
        bb_data = bb.create_bollinger_band(self.data)

        if 'CloseTime' not in bb_data.columns:
            bb_data['CloseTime'] = self.data['CloseTime']

        bb_data['CloseTime'] = pd.to_datetime(bb_data['CloseTime'], unit='ms')
        bb_data['CloseTime'] = bb_data['CloseTime'].view('int64') // 10 ** 9  # Convert to seconds

        # Make sure CloseTime is included in the final DataFrame before selecting other columns
        bb_data = bb_data[['CloseTime', 'signal']]  # Include CloseTime column

        bb_data.insert(0, 'symbol_id', np.ones(len(bb_data), dtype=np.int16) * symbol_id)
        bb_data.insert(1, 'asset_id', asset_id)

        bb_data.to_sql(f'bollingerBands_{self.interval}', self.connection, if_exists='append', index=False)

        # Print bb_data with CloseTime
        # print(bb_data)
        # print(input("Bollinger Band Data in going to enter in Database:"))

    def store_superTrend(self, symbol_id, asset_id):
        df = self.data.copy()

        # Ensure 'CloseTime' column is present
        if 'CloseTime' not in df.columns:
            df['CloseTime'] = self.data['CloseTime']

        df['CloseTime'] = pd.to_datetime(df['CloseTime'], unit='ms')
        df['CloseTime'] = df['CloseTime'].view('int64') // 10 ** 9  # Convert to seconds

        st = SuperTrend()
        st_data = st.create_super_trend(df)

        # Ensure 'CloseTime' column is present in st_data as well
        if 'CloseTime' not in st_data.columns:
            st_data['CloseTime'] = df['CloseTime']

        st_data['CloseTime'] = pd.to_datetime(st_data['CloseTime'], unit='ms')
        st_data['CloseTime'] = st_data['CloseTime'].view('int64') // 10 ** 9  # Convert to seconds

        # Make sure CloseTime is included in the final DataFrame before selecting other columns
        st_data = st_data[['CloseTime', 'signal']]  # Include CloseTime column

        st_data.insert(0, 'symbol_id', np.ones(len(st_data), dtype=np.int16) * symbol_id)
        st_data.insert(1, 'asset_id', asset_id)

        # Insert into database
        st_data.to_sql(f'superTrend_{self.interval}', self.connection, if_exists='append', index=False)

        # Print st_data with CloseTime
        # print(st_data)
        # print(input("Super Trend Data in going to enter in Database:"))


if __name__ == "__main__":
    from all_variable import Variable
    database = Variable.AI_DATABASE

    # Convert to absolute path
    absolute_path = os.path.abspath(database)
    script_name = os.path.basename(__file__)
    print(f"Database path: {absolute_path} and fine name: {script_name} ")
    # Connect or query to get the required input data for the Resample class
    connection = sqlite3.connect(database)
    query = f"SELECT * FROM asset_1"  # Replace `some_table_name` with the actual table you're querying
    data = pd.read_sql_query(query, connection)
    connection.close()
    print(data)
    print(input("Press Enter to continue...:"))
