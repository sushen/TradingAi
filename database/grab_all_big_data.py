"""
Get CSV Data : https://www.cryptodatadownload.com/data/binance/
"""

import sqlite3
import time
from database.dataframe import GetDataframe
import pickle
from exchange_info import BinanceExchange
import binance
import numpy as np
from indicator.candle_pattern import MakePattern

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
# fs = FindSymbols()
p_symbols = BinanceExchange()
all_symbols_payers = p_symbols.get_specific_symbols()

print("All symbols: ", len(all_symbols_payers))

# print(all_symbols_payers)
# symbol_data_already_collected

try:
    with open('symbol_data_already_collected.pkl', 'rb') as f:
        symbol_data_already_collected = pickle.load(f)
    print("symbol list loaded from file")
    print("Len of Symbol list: ",len(symbol_data_already_collected) )
except FileNotFoundError:
    print("symbol file not found, creating new list.")
    symbol_data_already_collected = []

# print(input(":"))

print(symbol_data_already_collected)
print("Symbols downloaded:", len(symbol_data_already_collected))
# print(input(":"))

for symbol in all_symbols_payers:

    if symbol in symbol_data_already_collected:
        continue
    print(symbol)
    # symbol = 'BTCBUSD'
    try:
        data = GetDataframe().get_minute_data(symbol, 1, time_of_data)
    except binance.exceptions.BinanceAPIException as e:
        print(f"Binance API exception: {e}")
        continue
    print(data)

    if data is None:
        print("Can not find any data for ", symbol)
        continue

    connection = sqlite3.connect("big_cripto.db")
    cur = connection.cursor()

    ###########################
    # Storing on symbol table #
    ###########################
    print("Storing data in symbol table")
    cur.execute("INSERT INTO symbols (symbolName) VALUES (?) RETURNING id", (symbol,))
    symbol_id = cur.fetchone()[0]
    connection.commit()
    cur.close()

    ##########################
    # Storing on asset table #
    ##########################
    print("Storing data in asset table")
    data.reset_index(inplace=True)  # Convert index to column
    time_col = data.pop('Time')  # Remove Time column and store it in variable
    data.insert(len(data.columns), 'Time', time_col)  # Insert Time column at the end

    data.drop("symbol", axis=1, inplace=True)
    change = data.pop("Change")
    data.insert(data.columns.get_loc(f'Volume{symbol[:-4]}') + 1, "Change", change)
    data.rename(columns={f'Volume{symbol[:-4]}': "Volume"}, inplace=True)
    data.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16)*symbol_id)
    print(data)

    connection = sqlite3.connect("big_cripto.db")
    cur = connection.cursor()
    data.to_sql('asset', connection, if_exists='append', index=False)

    #################################
    # Storing on criptoCandle table #
    #################################
    print("Storing data in criptoCandle table")
    make_pattern = MakePattern(data["Open"], data["High"], data["Low"], data["Close"])
    pattern = make_pattern.pattern()
    pattern.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    asset_ids = pd.read_sql(f"SELECT id FROM asset WHERE symbol_id = {symbol_id}", connection)['id']
    pattern.insert(1, 'cripto_id', asset_ids)
    pattern.to_sql('criptoCandle', connection, if_exists='append', index=False)

    ########################
    # Storing on rsi table #
    ########################
    # print("Storing data in rsi table")
    # rsi = make_pattern.rsi()
    # rsi.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    # rsi.insert(1, 'cripto_id', asset_ids)
    # rsi.to_sql('rsi', connection, if_exists='append', index=False)

    ##################################
    # Storing on movingAverage table #
    ##################################
    print("Storing data in rsi table")

    # Time Counting
    EndTime = time.time()
    print("\nThis Script End " + time.ctime())
    totalRunningTime = EndTime - StartTime
    print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
    print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")



    symbol_data_already_collected.append(symbol)
    with open('symbol_data_already_collected.pkl', 'wb') as f:
        pickle.dump(symbol_data_already_collected, f)
    print("The current loop is fully complete.")


    connection.commit()
    cur.close()



# print(input(":"))

# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")
