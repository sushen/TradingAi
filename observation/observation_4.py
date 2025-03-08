import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import numpy as np
from database_small.db_dataframe import GetDbDataframe
import matplotlib.pyplot as plt
import pandas as pd


def main(symbol):
    # Time Counting
    # start_time = time.time()
    # print("Script Start :", time.ctime())

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    total_sum = 900  # Updated total_sum to 1500
    lookback = 1440 * 30  # Lookback of 30 days (1440 minutes per day)

    # Updated times for specific time periods
    times = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]  # Time periods

    # Initialize a variable to store the sum
    total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))

    connection = sqlite3.connect("C:\\Users\\user\\PycharmProjects\\TradingAiVersion4\\database\\big_crypto_4years.db")
    db_frame = GetDbDataframe(connection)

    # Resample data for each time period and plot
    for time in times:
        resampled_data = db_frame.get_minute_data(symbol, time, lookback)
        df = db_frame.get_all_indicators(symbol, time, lookback)
        df.index = resampled_data.index
        resampled_data = resampled_data[~resampled_data.index.duplicated(keep='first')]
        df = df[~df.index.duplicated(keep='first')]
        resampled_data['sum'] = df.sum(axis=1)

        # Add the sum to the total sum
        print(time)
        print(resampled_data)
        total_sum_values = total_sum_values.add(resampled_data['sum'], fill_value=0)

    total_sum_values = total_sum_values.fillna(0).astype(np.int16)
    resampled_data = db_frame.get_minute_data(symbol, 1, lookback)
    resampled_data['sum'] = total_sum_values
    marker_sizes = np.abs(resampled_data['sum']) / 10

    # Plot the close price
    plt.figure(figsize=(14, 7))  # Set figure size for better visualization
    plt.plot(resampled_data['Close'], label='Close Price', color='blue', linewidth=1.5)

    # Buy and sell signal markers
    buy_indices = resampled_data.index[resampled_data['sum'] >= total_sum]
    sell_indices = resampled_data.index[resampled_data['sum'] <= -total_sum]

    plt.scatter(buy_indices, resampled_data['Close'][resampled_data['sum'] >= total_sum],
                marker='^', s=marker_sizes[resampled_data['sum'] >= total_sum], color='green', zorder=3,
                label='Buy Signal')
    plt.scatter(sell_indices, resampled_data['Close'][resampled_data['sum'] <= -total_sum],
                marker='v', s=marker_sizes[resampled_data['sum'] <= -total_sum], color='red', zorder=3,
                label='Sell Signal')

    # Add text labels for sum values
    for index in buy_indices:
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}',
                 ha='center', va='bottom', fontsize=8, color='green', fontweight='bold')
    for index in sell_indices:
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}',
                 ha='center', va='top', fontsize=8, color='red', fontweight='bold')

    # Time Counting
    # end_time = time.time()
    # print("End Time: ", end_time)
    # print("Script is running for " + str(int((end_time - start_time) / 60)) + " Minutes.")

    # Title and Labels
    plt.title(f'{symbol} Price with Buy/Sell Signals', fontsize=16)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust the layout to prevent clipping
    plt.show()


# Call the function for BTCUSDT
main("BTCUSDT")
