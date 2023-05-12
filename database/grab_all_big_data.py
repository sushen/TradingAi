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
from indicator.rsi import Rsi
from indicator.moving_average_signal import MovingAverage
from indicator.macd import Macd
from indicator.bollinger_bands import BollingerBand
from indicator.super_trend import SuperTrend
from create_resample_data import Resample
import warnings

warnings.filterwarnings("ignore")

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
    print("Len of Symbol list: ", len(symbol_data_already_collected))
except FileNotFoundError:
    print("symbol file not found, creating new list.")
    symbol_data_already_collected = []

# print(input(":"))

print(symbol_data_already_collected)
print("Symbols downloaded:", len(symbol_data_already_collected))
# print(input(":"))

for i, symbol in enumerate(all_symbols_payers):

    if symbol in symbol_data_already_collected:
        continue
    print(i, symbol)
    # symbol = 'BTCBUSD'
    # TODO: if you find trouble making symbol send it to find_symbols.py
    try:
        data = GetDataframe().get_minute_data(symbol, 1, time_of_data)
    except binance.exceptions.BinanceAPIException as e:
        print(f"Binance API exception: {e}")
        continue
    print(data)

    if data is None:
        print("Can not find any data for ", symbol)
        continue

    connection = sqlite3.connect("big_crypto.db")
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
    df = data.copy()
    df.reset_index(inplace=True)  # Convert index to column
    time_col = df.pop('Time')  # Remove Time column and store it in variable
    df.insert(len(df.columns), 'Time', time_col)  # Insert Time column at the end

    df.drop("symbol", axis=1, inplace=True)
    change = df.pop("Change")
    df.insert(df.columns.get_loc(f'Volume{symbol[:-4]}') + 1, "Change", change)
    df.rename(columns={f'Volume{symbol[:-4]}': "Volume"}, inplace=True)
    df.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)

    connection = sqlite3.connect("big_crypto.db")
    cur = connection.cursor()
    df.to_sql('asset_1m', connection, if_exists='append', index=False)

    # TODO: Make Class for every Indicator and think it like a package

    #################################
    # Storing on cryptoCandle table #
    #################################
    print("Storing data in cryptoCandle table")
    make_pattern = MakePattern()
    pattern = make_pattern.pattern(data)
    pattern.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    asset_ids = pd.read_sql(f"SELECT id FROM asset_1m WHERE symbol_id = {symbol_id}", connection)['id'].tolist()
    pattern.insert(1, 'asset_id', asset_ids)
    pattern.to_sql('cryptoCandle_1m', connection, if_exists='append', index=False)

    ########################
    # Storing on rsi table #
    ########################
    print("Storing data in rsi table")
    rsi = Rsi()
    rsi_data = rsi.create_rsi(data)
    rsi_data = rsi_data["signal"]
    rsi_data = rsi_data.to_frame()
    rsi_data.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    rsi_data.insert(1, 'asset_id', asset_ids)
    rsi_data.to_sql('rsi_1m', connection, if_exists='append', index=False)

    ##################################
    # Storing on movingAverage table #
    ##################################
    print("Storing data in movingAverage table")
    ma = MovingAverage()
    ma_data = ma.create_moving_average(data)
    ma_data = ma_data[['long_golden', 'short_medium', 'short_long', 'short_golden', 'medium_long', 'medium_golden']]
    ma_data.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    ma_data.insert(1, 'asset_id', asset_ids)
    ma_data.to_sql('movingAverage_1m', connection, if_exists='append', index=False)

    #########################
    # Storing on macd table #
    #########################
    print("Storing data in macd table")
    macd = Macd()
    macd_data = macd.create_macd(data)
    macd_data = macd_data['new_signal']
    macd_data = macd_data.to_frame()
    macd_data = macd_data.rename(columns={'new_signal': 'signal'})
    macd_data.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    macd_data.insert(1, 'asset_id', asset_ids)
    macd_data.to_sql('macd_1m', connection, if_exists='append', index=False)

    ###################################
    # Storing on bollinger band table #
    ###################################
    print("Storing data in bollinger band table")
    bb = BollingerBand()
    bb_data = bb.create_bollinger_band(data)
    bb_data = bb_data['signal']
    bb_data = bb_data.to_frame()
    bb_data.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    bb_data.insert(1, 'asset_id', asset_ids)
    bb_data.to_sql('bollingerBands_1m', connection, if_exists='append', index=False)

    ################################
    # Storing on super trend table #
    ################################
    print("Storing data in super trend table")
    df = data.copy()
    df = df.iloc[:, 1:7]
    df.rename(columns={'VolumeBTC': 'volume'}, inplace=True)
    df.index = df.index.rename('datetime')
    df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)

    st = SuperTrend()
    st_data = st.create_super_trend(df)
    st_data = st_data['signal']
    st_data = st_data.to_frame()
    st_data.insert(0, 'symbol_id', np.ones(len(data), dtype=np.int16) * symbol_id)
    st_data.insert(1, 'asset_id', asset_ids)
    st_data.to_sql('superTrend_1m', connection, if_exists='append', index=False)

    ######################################
    # Creating and storing resample data #
    ######################################
    print("Creating and storing resample data")
    resample = Resample(data)
    s_id = symbol_id
    resample.create_minute_data(s_id, symbol)

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
