import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
import sqlite3
from dataframe.db_dataframe import GetDbDataframe
from database_small.missing_data_single_symbol import MissingDataCollection
from playsound import playsound

from all_variable import Variable
# Set database path from Variable class
database = Variable.DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")


def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    target_symbol = "BTCUSDT"
    # missing_data = MissingDataCollection(database=database)
    # missing_data.collect_missing_data_single_symbols(target_symbol)
    # Specify symbol directly
    timeline = 1
    timelines = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
    lookback = 1440*30

    # Initialize an empty list to store DataFrames for each timeline
    all_Sum_data_frames = []
    for timeline in timelines:
        print(f"\nTimeline {timeline} minutes:")
        # Fetch the required symbol's information
        connection = sqlite3.connect(database)
        db_frame = GetDbDataframe(connection)
        data = db_frame.get_minute_data(target_symbol, timeline, lookback)
        df = db_frame.get_all_indicators(target_symbol, timeline, lookback)

        df.index = data.index  # Set the same index for df
        df = df.add_prefix(f"{timeline}_")
        data[f'Sum_{timeline}'] = df.sum(axis=1)
        # Add a column for the column names with non-zero values
        # data[f'Indicators{timeline}'] = df.apply(lambda row: [col for col in df.columns if row[col] != 0],
                                                        # axis=1)
        data[f'IndicatorsAndValues_{timeline}'] = df.apply(
            lambda row: [(col, row[col]) for col in df.columns if row[col] != 0], axis=1)

        # This time series does not matter
        total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
        total_sum_values = total_sum_values.add(data[f'Sum_{timeline}'], fill_value=0)


        total_sum_values = total_sum_values.fillna(0).astype(np.int16)
        df.fillna(0, inplace=True)
        data[f'Sum_{timeline}'] = total_sum_values

        data_frame = data[[f'Sum_{timeline}', f'IndicatorsAndValues_{timeline}']]
        all_Sum_data_frames.append(data_frame)


        print(data)
        # print(input("Input :"))

    # Concatenate all the DataFrames from different timelines into one DataFrame
    final_df = pd.concat(all_Sum_data_frames, axis=1)
    print(final_df)

    # total_sum = 800
    # # print(f"Symbol: {target_symbol} running in timeline: {timeline} minutes")
    # # print(f"Processing symbol: {target_symbol}")
    # print(f"Last 5 Signal for {target_symbol} above sum {total_sum} running in timeline: {timeline} minutes:")
    # print(data['sum'][-5:])
    # if not (any(data['sum'][-5:] >= total_sum) or any(data['sum'][-5:] <= -total_sum)):
    #     return
    #
    # buy_indices = data.index[data['sum'] >= total_sum]
    # sell_indices = data.index[data['sum'] <= -total_sum]
    #
    # for i, index in enumerate(buy_indices):
    #     if df.index.get_loc(index) >= len(df) - 5:
    #         p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
    #         p = f"Sum: {data['sum'][index]}  indicators: {', '.join(p_cols)}"
    #         print(p)
    #
    #         print("The Bullish sound")
    #         playsound(r'../sounds/Bullish.wav')
    #
    #
    # for i, index in enumerate(sell_indices):
    #     if df.index.get_loc(index) >= len(df) - 5:
    #         p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
    #         p = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(p_cols)}"
    #         print(p)
    #
    #         print("The Bearish sound")
    #         playsound(r'../sounds/Bearish.wav')

main()

