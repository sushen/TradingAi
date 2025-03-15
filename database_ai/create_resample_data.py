"""
Script Name: create_resample_data.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

import sqlite3
import pandas as pd
import numpy as np
from store_in_db import StoreData
from resample import ResampleData
from indicator.candle_pattern import MakePattern
from indicator.rsi import Rsi
from indicator.moving_average_signal import MovingAverage
from indicator.macd import Macd
from indicator.bollinger_bands import BollingerBand
from indicator.super_trend import SuperTrend

from all_variable import Variable
# Set database path from Variable class
database = Variable.AI_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")


database = database

class Resample:
    def __init__(self, data):
        self.data = data
        self.rb = ResampleData()
        # self.minute_data = [3, 5]
        self.minute_data = [3, 5, 15, 30, 60, 4*60, 24*60, 7*24*60]
        self.connection = sqlite3.connect(database)

    def create_minute_data(self, s_id, symbol):
        for minute in self.minute_data:
            print(f"\nProcessing {minute} minute data...")

            ##########################
            # Storing on asset table #
            ##########################
            print(f"Resampling Asset Table for {minute} minutes")

            # Ensure 'CloseTime' is part of the DataFrame and convert it to datetime
            df_ = self.data.rename_axis('CloseTime_index')
            df_['CloseTime'] = df_.index.astype('int64') // 10 ** 6  # Convert index to Unix timestamp (milliseconds)

            rd = ResampleData(symbol)
            asset_data = rd.resample_to_minute(df_, minute)

            # Drop the 'symbol' column if it exists and insert symbol_id
            asset_data.drop("symbol", axis=1, inplace=True, errors='ignore')
            symbol_id = np.ones(len(asset_data), dtype=np.int16) * s_id
            asset_data.insert(0, 'symbol_id', symbol_id)

            # Store the resampled data in the database
            asset_data.to_sql(name=f'asset_{minute}', con=self.connection, if_exists='append', index=False)
            print(f"Asset Data for {minute} minutes stored.")

            #################################
            # Storing on cryptoCandle table #
            #################################
            print(f"Resampling cryptoCandle Table for {minute} minutes")

            # Use the store_cryptoCandle method from StoreData class to store the candle data
            store_data = StoreData(asset_data, self.connection, None, symbol, minute)  # Pass minute interval here
            store_data.store_cryptoCandle(s_id, None)  # Pass asset_id if available (or handle as None)

            ########################
            # Storing on RSI table #
            ########################
            print(f"Storing data in RSI table for {minute} minutes")
            store_data.store_rsi(s_id, None)

            ##################################
            # Storing on MovingAverage table #
            ##################################
            print(f"Storing data in MovingAverage table for {minute} minutes")
            store_data.store_movingAverage(s_id, None)

            #########################
            # Storing on MACD table #
            #########################
            print(f"Storing data in MACD table for {minute} minutes")
            store_data.store_macd(s_id, None)

            ###################################
            # Storing on Bollinger Bands table #
            ###################################
            print(f"Storing data in Bollinger Bands table for {minute} minutes")
            store_data.store_bollingerBand(s_id, None)

            ################################
            # Storing on SuperTrend table #
            ################################
            print(f"Storing data in SuperTrend table for {minute} minutes")
            store_data.store_superTrend(s_id, None)

            # Commit the data for this interval
            self.connection.commit()
            print(f"Data for {minute} minute interval successfully stored.\n")


if __name__ == "__main__":
    # Connect or query to get the required input data for the Resample class
    connection = sqlite3.connect(database)
    query = f"SELECT * FROM asset_1"  # Replace `some_table_name` with the actual table you're querying
    data = pd.read_sql_query(query, connection)
    connection.close()
    print(data.head())
    # print(input("Press Enter to continue..."))
    # Initialize Resample object
    resample = Resample(data)

    # Resample 1-minute data into the specified time intervals
    # time_intervals = [3, 5, 15, 30, 60, 240, 1440, 10080]  # Specified intervals in minutes

    # for interval in time_intervals:
    print(f"Resampling data to minutes.")
    resample.create_minute_data(1, "BTCUSDT")