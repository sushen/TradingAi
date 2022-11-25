"""
Get CSV Data : https://www.cryptodatadownload.com/data/binance/
"""

import sqlite3
import time
from datetime import datetime

import pandas as pd

from pandas import Timestamp

from connection import create_connection

from dataframe import GetDataframe

total_years = 1
months = 1 * total_years
days = 1 * months
hours = 24 * days
minute = hours * 60
print(f"We are grabbing '{minute}' candles")
# print(input("Find Minutes:"))
time_of_data = int(minute)

# Time Counting
StartTime = time.time()
print("This Script Start " + time.ctime())

symbol = 'BTCBUSD'
data = GetDataframe().get_minute_data(symbol, 1, time_of_data)
print(data)

# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")

# print(input("All Minutes Data :"))
connection = sqlite3.connect("cripto.db")
cur = connection.cursor()

for i in range(len(data)):
    # print(single_data)
    open_position = data['Open'].iloc[i]
    high_position = data['High'].iloc[i]
    low_position = data['Low'].iloc[i]
    close_position = data['Close'].iloc[i]

    symbol_volume_position = data[f'Volume{symbol[:-4]}'].iloc[i]
    close_time = data['CloseTime'].iloc[i]
    trades = data['Trades'].iloc[i]
    buy_quote_volume = data['BuyQuoteVolume'].iloc[i]

    change_position = data['Change'].iloc[i]
    symbol_position = data['symbol'].iloc[i]
    time_position = data.index[i]
    unix_time = time_position.timestamp()
    print(f"{open_position}, {high_position}, {low_position}, {close_position}, {symbol_volume_position},{int(close_time)}, {trades}, {buy_quote_volume}, {change_position}, {symbol_position}, {time_position}, {int(unix_time)}")

    cur.execute(
        "INSERT INTO asset VALUES (:id, :symbol, :Open, :High, :Low,  :Close, :VolumeBTC, :Change , :CloseTime, :Trades, :BuyQuoteVolume, :Time  )",
        {
            'id': None,
            'symbol': symbol,
            'Open': open_position,
            'High': high_position,
            'Low': low_position,
            'Close': close_position,
            'VolumeBTC': symbol_volume_position,
            'Change': change_position,
            'CloseTime': int(close_time),
            'Trades': trades,
            'BuyQuoteVolume': buy_quote_volume,
            'Time': int(unix_time)
        })
connection.commit()
cur.close()


# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")