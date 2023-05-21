import sqlite3
import numpy as np
from database.db_dataframe import GetDbDataframe
import matplotlib.pyplot as plt


def main(symbol):
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    total_sum = 800
    lookback = 30*1440
    times = [1, 3, 5, 15, 30]  # Time periods

    # Initialize a variable to store the sum
    total_sum_values = 0
    connection = sqlite3.connect("../database/big_crypto.db")
    db_frame = GetDbDataframe(connection)

    # Resample data for each time period and plot
    for time in times:

        resampled_data = db_frame.get_minute_data(symbol, time, lookback)
        df = db_frame.get_all_indicators(symbol, time, lookback)
        df.index = resampled_data.index
        resampled_data['sum'] = df.sum(axis=1)

        # Add the sum to the total sum
        total_sum_values += resampled_data['sum']

    total_sum_values.fillna(0, inplace=True)
    total_sum_values = total_sum_values.astype(np.int16)
    resampled_data = db_frame.get_minute_data(symbol, 1, lookback)
    resampled_data['sum'] = total_sum_values
    marker_sizes = np.abs(resampled_data['sum']) / 10
    plt.plot(resampled_data['Close'], label='Close Price')
    buy_indices = resampled_data.index[resampled_data['sum'] >= total_sum]
    sell_indices = resampled_data.index[resampled_data['sum'] <= -total_sum]
    plt.scatter(buy_indices, resampled_data['Close'][resampled_data['sum'] >= total_sum],
                marker='^', s=marker_sizes[resampled_data['sum'] >= total_sum], color='green',
                zorder=3)
    plt.scatter(sell_indices, resampled_data['Close'][resampled_data['sum'] <= -total_sum],
                marker='v', s=marker_sizes[resampled_data['sum'] <= -total_sum], color='red',
                zorder=3)
    # Add text labels for sum values
    for index in buy_indices:
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}',
                 ha='center', va='bottom', fontsize=8)
    for index in sell_indices:
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}',
                 ha='center', va='top', fontsize=8)

    plt.title(symbol)
    plt.legend()
    plt.grid(True)
    plt.show()


main("BTCBUSD")
