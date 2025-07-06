"""
Script Name: grab_data.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import time
import pickle
import binance

from dataframe.dataframe import GetDataframe
from dataframe.future_dataframe import GetFutureDataframe
from exchange.exchange_info import BinanceExchange
from database.create_resample_data import Resample
from database.store_in_db import StoreData
import warnings

warnings.filterwarnings("ignore")

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

from all_variable import Variable
# Set database path from Variable class
database = Variable.DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")

class DataCollection:
    def __init__(self):
        #TODO :Grabbing Data Calculation I need to measure before I pull big data and measure

        # self.total_years = 4/128 # This is 1.5 month Data work within 1 minutes
        self.total_years = 2
        self.months = 12 * self.total_years
        self.days = 30 * self.months
        self.hours = 24 * self.days
        self.minute = self.hours * 60
        print(f"We are grabbing '{self.minute}' candles")
        self.time_of_data = int(self.minute)
        self.time_of_finishing_data_processing = self.time_of_data * 0.004652777777777777
        print(f"We need {self.time_of_finishing_data_processing} seconds or {self.time_of_finishing_data_processing/60} minutes to process total data ")

        self.StartTime = time.time()
        print("This Script Start " + time.ctime())

    def collect_data(self, symbol):

        data = GetFutureDataframe().get_minute_data(symbol, 1, self.time_of_data)

        ApiDataCollectionEndTime = time.time()
        print("\nCandle Data Collection End " + time.ctime())
        ApiDataCollectionTotalRunningTime = ApiDataCollectionEndTime - self.StartTime
        print(f"Collect Candle Data from Api in {ApiDataCollectionTotalRunningTime} Seconds and {ApiDataCollectionTotalRunningTime/60} minutes")

        connection = sqlite3.connect(database)
        cur = connection.cursor()

        store_data = StoreData(data, connection, cur, symbol)
        print("Storing data in symbol table")
        symbol_id = store_data.store_symbol()

        print("Storing data in asset table")
        store_data.store_asset(symbol_id)

        print("Storing data in cryptoCandle table")
        asset_id = store_data.store_cryptoCandle(symbol_id)

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

        print("Storing data in fibonacci retracement table")
        store_data.store_fibonacciRetracement(symbol_id, asset_id)


        print("Creating and storing resample data")
        resample = Resample(data)
        s_id = symbol_id
        resample.create_minute_data(s_id, symbol)


        connection.commit()
        cur.close()

        EndTime = time.time()
        print("\nThis Script End " + time.ctime())
        totalRunningTime = EndTime - self.StartTime
        print("This Script is running for " + str(int(totalRunningTime)) + " Seconds.")



if __name__ == "__main__":
    data_collection = DataCollection()
    data_collection.collect_data("BTCUSDT")