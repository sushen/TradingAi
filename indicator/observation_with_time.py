import time
import numpy as np
from database.dataframe import GetDataframe
import matplotlib.pyplot as plt
from indicator.indicators import CreateIndicators
import binance
from network.network_status import BinanceNetwork
from database.resample import ResampleData

#
#  Reason: False Signal
#  Reasoning: Signal Comes from 1 minutes data and its give True projection for next 5 to 10 minutes
#  We need to add 3 , 5 , 15 , 30 minutes data to see future projection

def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    bn = BinanceNetwork()
    server_time = bn.get_server_time()
    print("Server time: ", server_time)
    time_diff = bn.get_time_diff()
    print(f"The time difference between server and local machine is {time_diff:.2f} seconds")

    total_sum = 800
    symbol = "BTCBUSD"
    lookback = 2880
    times = [1, 3, 5, 10, 15, 30]  # Time periods

    try:
        data = GetDataframe().get_minute_data(f'{symbol}', 1, lookback)
    except binance.exceptions.BinanceAPIException as e:
        print(f"Binance API exception: {e}")

    data = data.rename_axis('Time_index')
    data['Time'] = data.index

    # Resample data for each time period and plot
    for time in times:
        if time > 1:
            rd = ResampleData(symbol)
            resampled_data = rd.resample_to_minute(data, time)
        else:
            resampled_data = data.copy()

        ci = CreateIndicators(resampled_data)
        df = ci.create_all_indicators()
        resampled_data['sum'] = df.sum(axis=1)

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

main()
