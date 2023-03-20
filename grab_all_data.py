"""
Get CSV Data : https://www.cryptodatadownload.com/data/binance/
"""

import sqlite3
import time
from dataframe import GetDataframe

total_years = 1
months = 1 * total_years
days = 1 * months
hours = 1 * days
minute = hours * 1
print(f"We are grabbing '{minute}' candles")
# print(input("Find Minutes:"))
time_of_data = int(minute)

# Time Counting
StartTime = time.time()
print("This Script Start " + time.ctime())

from get_symbol.find_symbols import FindSymbols
import pandas as pd
pd.set_option('mode.chained_assignment', None)
#
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)
#
from api_callling.api_calling import APICall
ticker_info = pd.DataFrame(APICall.client.get_ticker())
# print(ticker_info)
fs = FindSymbols()
all_symbols_payers = fs.get_all_symbols("BUSD", ticker_info)['symbol']

# print(all_symbols_payers)

for symbol in all_symbols_payers:
    print(symbol)

    # symbol = 'BTCBUSD'
    data = GetDataframe().get_minute_data(symbol, 1, time_of_data)
    print(data)

    # Time Counting
    EndTime = time.time()
    print("\nThis Script End " + time.ctime())
    totalRunningTime = EndTime - StartTime
    print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
    print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")

    # print(input("All Minutes Data :"))
    # connection = sqlite3.connect("big_data.db")
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
        VolumeBUSD = data['VolumeBUSD'].iloc[i]
        trades = data['Trades'].iloc[i]
        buy_quote_volume = data['BuyQuoteVolume'].iloc[i]

        change_position = data['Change'].iloc[i]
        symbol_position = data['symbol'].iloc[i]
        time_position = data.index[i]
        unix_time = time_position.timestamp()
        # print(f"{open_position}, {high_position}, {low_position}, {close_position}, {symbol_volume_position},{int(close_time)}, {VolumeBUSD}, {trades}, {buy_quote_volume}, {change_position}, {symbol_position}, {time_position}, {int(unix_time)}")
        # print(input("...:"))
        cur.execute(
            "INSERT INTO asset VALUES (:id, :symbol, :Open, :High, :Low,  :Close, :VolumeBTC, :Change , :CloseTime, :VolumeBUSD, :Trades, :BuyQuoteVolume, :Time )",
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
                'VolumeBUSD': float(VolumeBUSD),
                'Trades': trades,
                'BuyQuoteVolume': buy_quote_volume,
                'Time': int(unix_time)
            })

    connection.commit()
    cur.close()

#print(input(":"))



# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")
