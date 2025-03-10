"""
Script Name: grab_data.py
Author: Sushen Biswas
Date of Creation: 2023-10-30
Last Update: 2025-03-10
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

import sqlite3
import time
import logging
import pandas as pd
import binance
from dataframe import GetDataframe
from future_dataframe import GetFutureDataframe
from exchange_info import BinanceExchange
from create_resample_data import Resample
from store_in_db import StoreData
from api_callling.api_calling import APICall
import warnings
warnings.filterwarnings("ignore")

from all_variable import Variable
# Set database path from Variable class
database = Variable.AI_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")

# Create a connection to the database
conn = sqlite3.connect(database)  # Adjust database file name if needed

# Setup Minimal Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("data_collection.log", mode="a"),
        logging.StreamHandler()
    ]
)
logging.info("Starting Data Collection")

database = database

class DataCollection:
    def __init__(self):
        self.months = 1
        self.days = 30 * self.months
        self.hours = 24 * self.days
        self.minute = self.hours * 60
        self.time_of_data = int(self.minute)
        self.symbol = "BTCUSDT"

        self.StartTime = time.time()
        logging.info(f"We are grabbing '{self.minute}' candles.")
        logging.info("Script Start Time: " + time.ctime())

    def collect_data(self, symbol):
        try:
            data = GetFutureDataframe().get_minute_data(symbol, 1, self.time_of_data)
            print(f"Data from Binance:{data}")

            # Logging completion of symbol processing
            EndTime = time.time()
            totalRunningTime = EndTime - self.StartTime
            logging.info(f"Completed {symbol} Data Downloading in : {int(totalRunningTime / 60)} minutes.")
            # print(input("Got The data from Binance: "))
        except binance.exceptions.BinanceAPIException as e:
            logging.error(f"Binance API error for {symbol}: {e}")
            print(input(f"Binance API error for {symbol}"))

        if data is None:
            logging.warning(f"No data for {symbol},")


        connection = sqlite3.connect(database)
        cur = connection.cursor()
        store_data = StoreData(data, connection, cur, symbol)

        # Storing symbol data
        symbol_id = store_data.store_symbol()

        # Storing asset data
        store_data.store_asset(symbol_id)

        # Storing cryptoCandle data
        asset_id = store_data.store_cryptoCandle(symbol_id)

        # Storing RSI, Moving Average, MACD, Bollinger Bands, Super Trend data
        store_data.store_rsi(symbol_id, asset_id)
        store_data.store_movingAverage(symbol_id, asset_id)
        store_data.store_macd(symbol_id, asset_id)
        store_data.store_bollingerBand(symbol_id, asset_id)
        store_data.store_superTrend(symbol_id, asset_id)

        # Creating and storing resample data
        resample = Resample(data)
        resample.create_minute_data(symbol_id, symbol)

        connection.commit()
        cur.close()

        # Logging completion of symbol processing
        EndTime = time.time()
        totalRunningTime = EndTime - self.StartTime
        logging.info(f"Completed {symbol}. Total runtime for symbol: {int(totalRunningTime / 60)} minutes.")

    logging.info("Data Collection Completed.")

if __name__ == "__main__":
    data_collection = DataCollection()
    data_collection.collect_data("BTCUSDT")
