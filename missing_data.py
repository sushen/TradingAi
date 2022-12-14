"""
Get CSV Data : https://www.cryptodatadownload.com/data/binance/
"""

import pprint
import sqlite3
import time
from datetime import datetime

from dataframe import GetDataframe


# Time Counting
StartTime = time.time()
print("This Script Start " + time.ctime())

symbol = 'BTCBUSD'
connection = sqlite3.connect("big_data.db")
cur = connection.cursor()

last_db_close_time = cur.execute("select CloseTime from asset order by CloseTime desc limit 1").fetchone()[0]
current_time = str(datetime.utcnow())

data = GetDataframe().get_range_data(symbol, 1, last_db_close_time, current_time)
# data  = pd.DataFrame(APICall.client.get_historical_klines(symbol, APICall.client.KLINE_INTERVAL_1MINUTE, last_db_close_time, current_time)
# )

pprint.pprint(data)


# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")


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
    print(f"{open_position}, {high_position}, {low_position}, {close_position}, {symbol_volume_position},{int(close_time)}, {VolumeBUSD}, {trades}, {buy_quote_volume}, {change_position}, {symbol_position}, {time_position}, {int(unix_time)}")
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


# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")
