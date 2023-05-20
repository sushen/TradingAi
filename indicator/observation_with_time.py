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

    # Resample data for each time period and plot
    for time in times:

        connection = sqlite3.connect("../database/big_crypto1.db")
        db_frame = GetDbDataframe(connection)
        resampled_data = db_frame.get_minute_data(symbol, time, lookback)
        resampled_data = resampled_data.drop('symbol', axis=1)
        resampled_data = resampled_data.astype(np.float32)

        df = db_frame.get_all_indicators(symbol, time, lookback)
        df.index = resampled_data.index
        df = df.astype(np.int16)
        resampled_data['sum'] = df.sum(axis=1)
        print(resampled_data)

        marker_sizes = np.abs(resampled_data['sum']) / 10

        if time == 1:
            # Plot close price for time = 1
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
            plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}\n{time}-minute',
                     ha='center', va='bottom', fontsize=8)
        for index in sell_indices:
            plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}\n{time}-minute',
                     ha='center', va='top', fontsize=8)

    # Instate of Figure write Symbol name
    plt.title(symbol)
    plt.legend()
    plt.show()

main("BTCBUSD")
