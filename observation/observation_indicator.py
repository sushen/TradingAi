import sys
import os
import sqlite3
import numpy as np
import pandas as pd
import time
from database_small.db_dataframe import GetDbDataframe
from all_variable import Variable

# Constants
# Set database path from Variable class
database = Variable.SMALL_DATABASE
# database = Variable.BIG_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
print(f"Database path: {absolute_path}")

TOTAL_SUM = 500  # Adjust the sum threshold to your needs
TIME_PERIODS = [1, 3, 5, 15, 30, 60, 240, 1440, 10080]  # Time periods in minutes

# Setup
def get_database_connection():
    connection = sqlite3.connect(database)
    return connection

# Fetch data
def fetch_resampled_data(symbol, time_period, db_frame):
    print(f"Fetching data for {symbol} at {time_period} minutes...")

    resampled_data = db_frame.get_minute_data(symbol, time_period, 90)
    df = db_frame.get_all_indicators(symbol, time_period, 90)

    if resampled_data.empty or df.empty:
        print(f"No data found for {symbol} at {time_period} minutes!")
        return None, None

    df.index = resampled_data.index
    resampled_data = resampled_data[~resampled_data.index.duplicated(keep='first')]
    df = df[~df.index.duplicated(keep='first')]

    return resampled_data, df

# Print indicator values
def print_indicator_values(resampled_data, df):
    if df is None:
        print("DataFrame is None. Skipping this timeframe.")
        return

    for index in resampled_data.index:
        p_cols = [f'{col}({df.loc[index, col]:.2f})' for col in df.columns if df.loc[index, col] != 0]
        p = f"Sum: {resampled_data['sum'].loc[index]}  Non-zero indicators: {', '.join(p_cols)}"
        print(p)

# Main function
def main(symbol):
    connection = get_database_connection()
    db_frame = GetDbDataframe(connection)

    for time in TIME_PERIODS:
        resampled_data, df = fetch_resampled_data(symbol, time, db_frame)
        if resampled_data is None or df is None:
            continue
        resampled_data['sum'] = df.sum(axis=1)
        print_indicator_values(resampled_data, df)

# Call main function
if __name__ == "__main__":
    main("BTCUSDT")  # Replace with your symbol
