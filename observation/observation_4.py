"""
Script Name: observation.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from all_variable import Variable
from database_small.db_dataframe import GetDbDataframe

# Set database path from Variable class
# database = Variable.SMALL_DATABASE
database = Variable.BIG_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
print(f"Database path: {absolute_path}")

# Initialize global constants
LOOKBACK = 1440 * 30 * 12  # Lookback of 1 year (1440 minutes per day)
TOTAL_SUM = 900  # Updated total_sum to 1500
TIME_PERIODS = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]  # Time periods

def get_database_connection():
    """Returns a connection to the SQLite database."""
    connection = sqlite3.connect(database)
    return connection

def fetch_resampled_data(symbol, time_period, lookback, db_frame):
    """Fetches resampled data and indicators for a given time period."""
    resampled_data = db_frame.get_minute_data(symbol, time_period, lookback)
    df = db_frame.get_all_indicators(symbol, time_period, lookback)
    df.index = resampled_data.index
    resampled_data = resampled_data[~resampled_data.index.duplicated(keep='first')]
    df = df[~df.index.duplicated(keep='first')]
    return resampled_data, df

def calculate_total_sum(resampled_data, df):
    """Calculates the total sum of indicators and adds it to the resampled data."""
    resampled_data['sum'] = df.sum(axis=1)
    return resampled_data

def plot_signals(resampled_data, total_sum_values, symbol):
    """Plots the close price along with buy and sell signals."""
    marker_sizes = np.abs(resampled_data['sum']) / 10

    # Plot the close price
    plt.figure(figsize=(14, 7))  # Set figure size for better visualization
    plt.plot(resampled_data['Close'], label='Close Price', color='blue', linewidth=1.5)

    # Buy and sell signal markers
    buy_indices = resampled_data.index[resampled_data['sum'] >= TOTAL_SUM]
    sell_indices = resampled_data.index[resampled_data['sum'] <= -TOTAL_SUM]

    plt.scatter(buy_indices, resampled_data['Close'][resampled_data['sum'] >= TOTAL_SUM],
                marker='^', s=marker_sizes[resampled_data['sum'] >= TOTAL_SUM], color='green', zorder=3,
                label='Buy Signal')
    plt.scatter(sell_indices, resampled_data['Close'][resampled_data['sum'] <= -TOTAL_SUM],
                marker='v', s=marker_sizes[resampled_data['sum'] <= -TOTAL_SUM], color='red', zorder=3,
                label='Sell Signal')

    # Add text labels for sum values
    for index in buy_indices:
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}',
                 ha='center', va='bottom', fontsize=8, color='green', fontweight='bold')
    for index in sell_indices:
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}',
                 ha='center', va='top', fontsize=8, color='red', fontweight='bold')

    # Title and Labels
    plt.title(f'{symbol} Price with Buy/Sell Signals', fontsize=16)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust the layout to prevent clipping
    plt.show()

def main(symbol):
    """Main function to run the entire process."""
    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # Get database connection and fetch data
    connection = get_database_connection()
    db_frame = GetDbDataframe(connection)

    total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))

    # Resample data for each time period and accumulate the sum
    for time in TIME_PERIODS:
        resampled_data, df = fetch_resampled_data(symbol, time, LOOKBACK, db_frame)
        resampled_data = calculate_total_sum(resampled_data, df)

        # Add the sum to the total sum
        total_sum_values = total_sum_values.add(resampled_data['sum'], fill_value=0)

    total_sum_values = total_sum_values.fillna(0).astype(np.int16)

    # Final resampled data and plot
    resampled_data = db_frame.get_minute_data(symbol, 1, LOOKBACK)
    resampled_data['sum'] = total_sum_values

    # Corrected function call: pass `symbol` as the third argument
    plot_signals(resampled_data, total_sum_values, symbol)


# Call the function for BTCUSDT
if __name__ == "__main__":
    main("BTCUSDT")
