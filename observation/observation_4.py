import sys
import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from all_variable import Variable
from database_small.db_dataframe import GetDbDataframe

# Constants
LOOKBACK = 1440 / 32  # Lookback of 1 year (1440 minutes per day)
TOTAL_SUM = 500  # Sum threshold for signals
TIME_PERIODS = [1, 3, 5, 15, 30]  # Simplified time periods for testing

# Set database path from Variable class
database = Variable.SMALL_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
print(f"Database path: {absolute_path}")


# Setup database connection
def get_database_connection():
    connection = sqlite3.connect(database)
    return connection


# Fetch resampled data and indicators
def fetch_resampled_data(symbol, time_period, db_frame, lookback):
    print(f"Fetching data for {symbol} at {time_period} minutes...")
    resampled_data = db_frame.get_minute_data(symbol, time_period, lookback)
    df = db_frame.get_all_indicators(symbol, time_period, lookback)

    print(f"Fetched {len(resampled_data)} rows of resampled data.")
    print(f"Fetched {len(df)} rows of indicator data.")

    if resampled_data.empty or df.empty:
        print(f"No data found for {symbol} at {time_period} minutes!")
        return None, None

    df.index = resampled_data.index
    resampled_data = resampled_data[~resampled_data.index.duplicated(keep='first')]
    df = df[~df.index.duplicated(keep='first')]

    return resampled_data, df


# Calculate the total sum of indicators, filtering out NaN values
def calculate_total_sum(resampled_data, df):
    df_cleaned = df.dropna(axis=1, how='any')  # Drop columns that have NaN values in any row
    resampled_data['sum'] = df_cleaned.sum(axis=1)
    return resampled_data


# Function to fetch columns with exact values of 100 or -100
def get_indicator_columns(df, resampled_data):
    valid_columns = []

    # Ensure index alignment by checking the timestamp before accessing
    for index in resampled_data.index:
        if index in df.index:  # Ensure the index exists in both DataFrames
            # Loop through columns and check if the value is 100 or -100
            valid_columns += [
                col for col in df.columns if df[col].loc[index] == 100 or df[col].loc[index] == -100
            ]
    return valid_columns


# Print indicator values for buy/sell signals, excluding NaN values
def print_indicators_and_sum(resampled_data, df, total_sum_values, symbol):
    if df is None or df.empty:
        print("DataFrame is None or empty. Skipping this timeframe.")
        return

    df = df.reindex(resampled_data.index)
    print(f"Indicators for {symbol}:")

    for index in resampled_data.index:
        contributing_indicators = [
            f'{col}({df[col].loc[index]:.2f})' for col in df.columns
            if not np.isnan(df[col].loc[index]) and (df[col].loc[index] == 100 or df[col].loc[index] == -100)
        ]

        if contributing_indicators:
            print(f"At {index}, Sum: {total_sum_values[index]}  Indicators: {', '.join(contributing_indicators)}")

        if total_sum_values[index] >= TOTAL_SUM:
            print(f"Buy Signal at {index}")
        elif total_sum_values[index] <= -TOTAL_SUM:
            print(f"Sell Signal at {index}")
        else:
            print(f"No buy/sell signal at {index}")


# Main function to run the entire process
def main(symbol):
    connection = get_database_connection()
    db_frame = GetDbDataframe(connection)

    total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))

    for time in TIME_PERIODS:
        resampled_data, df = fetch_resampled_data(symbol, time, db_frame, LOOKBACK)
        if resampled_data is None or df is None:
            continue
        resampled_data = calculate_total_sum(resampled_data, df)
        total_sum_values = total_sum_values.add(resampled_data['sum'], fill_value=0)

    total_sum_values = total_sum_values.fillna(0).astype(np.int16)

    resampled_data = db_frame.get_minute_data(symbol, 1, LOOKBACK)
    resampled_data['sum'] = total_sum_values

    valid_columns = get_indicator_columns(df, resampled_data)
    print(f"Columns with 100/-100 values: {valid_columns}")

    print_indicators_and_sum(resampled_data, df, total_sum_values, symbol)


# Run the main function for a symbol (e.g., BTCUSDT)
if __name__ == "__main__":
    main("BTCUSDT")
