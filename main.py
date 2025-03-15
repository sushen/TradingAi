import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Print script name
script_name = os.path.basename(__file__)
print(f"fine name: {script_name}")

import time
import numpy as np
import sqlite3
from database_ai.db_dataframe import GetDbDataframe
from database.exchange_info import BinanceExchange
from datetime import datetime
from database_ai.missing_data_single_symbol import MissingDataCollection
from playsound import playsound

from all_variable import Variable
# Set database path from Variable class
database = Variable.AI_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
print(f"Database path: {absolute_path}")

def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # Specify symbol directly
    target_symbol = "BTCUSDT"

    # Ensure the method is correctly called from MissingDataCollection
    missing_data = MissingDataCollection(database=database)
    missing_data.collect_missing_data_single_symbols(target_symbol)  # This should work if the method is defined properly

    print(f"Processing symbol: {target_symbol}")

    # Fetch the required symbol's information
    connection = sqlite3.connect(database)
    db_frame = GetDbDataframe(connection)
    data = db_frame.get_minute_data(target_symbol, 1, 90)
    df = db_frame.get_all_indicators(target_symbol, 1, 90)
    df.index = data.index
    df = df.add_prefix("1_")
    data['sum'] = df.sum(axis=1)
    times = [3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
    total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
    total_sum_values = total_sum_values.add(data['sum'], fill_value=0)

    for time in times:
        temp_data = db_frame.get_minute_data(target_symbol, time, 90)
        temp_df = db_frame.get_all_indicators(target_symbol, time, 90)
        temp_df.index = temp_data.index
        temp_data = temp_data[~temp_data.index.duplicated(keep='first')]
        temp_df = temp_df[~temp_df.index.duplicated(keep='first')]
        temp_df = temp_df.add_prefix(f"{time}m_")
        df = pd.concat([df, temp_df], axis=1)
        temp_data['sum'] = temp_df.sum(axis=1)
        total_sum_values = total_sum_values.add(temp_data['sum'], fill_value=0)

        # Print last 5 sum for each timeframe
        print(f"Last 5 sum for {time}m:")
        print(temp_data['sum'][-5:])

    total_sum_values = total_sum_values.fillna(0).astype(np.int16)
    df.fillna(0, inplace=True)
    data['sum'] = total_sum_values

    total_sum = 200

    print("Last 5 overall sum:")
    print(data['sum'][-5:])
    if not (any(data['sum'][-5:] >= total_sum) or any(data['sum'][-5:] <= -total_sum)):
        return

    buy_indices = data.index[data['sum'] >= total_sum]
    sell_indices = data.index[data['sum'] <= -total_sum]

    for i, index in enumerate(buy_indices):
        if df.index.get_loc(index) >= len(df) - 5:
            p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
            p = f"Sum: {data['sum'][index]}  indicators: {', '.join(p_cols)}"

            print("The Bullish sound")
            playsound('C:\\Users\\user\PycharmProjects\TradingAiVersion3\sounds\Bullish.wav')
            playsound('C:\\Users\\user\PycharmProjects\TradingAiVersion3\sounds\Bullish Voice.mp3')

            print(p)
    for i, index in enumerate(sell_indices):
        if df.index.get_loc(index) >= len(df) - 5:
            p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
            p = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(p_cols)}"

            print("The Bearish sound")
            playsound('C:\\Users\\user\PycharmProjects\TradingAiVersion3\sounds\Bearish.wav')
            playsound('C:\\Users\\user\PycharmProjects\TradingAiVersion3\sounds\Bearish Voice.mp3')

            print(p)

# main()
while True:
    main()
    time.sleep(60)
