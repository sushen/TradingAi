import time
import numpy as np
from database.dataframe import GetDataframe
import matplotlib.pyplot as plt
from indicator.indicators import CreateIndicators
import binance
from network.network_status import BinanceNetwork
from database.resample import ResampleData

# TODO :
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
    symbol = "BTCBUSD"    #AGIXBUSD
    lookback = 1440
    time = 3            # For 3 minute data

    try:
        data = GetDataframe().get_minute_data(f'{symbol}', 1, lookback)
    except binance.exceptions.BinanceAPIException as e:
        print(f"Binance API exception: {e}")

    if time > 1:
        rd = ResampleData(symbol)
        data = rd.resample_to_minute(data, time)

    # print(data)
    ci = CreateIndicators(data)
    # print("All Indicators: ")
    df = ci.create_all_indicators()
    # print(df)
    data['sum'] = df.sum(axis=1)

    # print(data)

    marker_sizes = np.abs(data['sum']) / 10
    # Add Buy and Sell signals


    # Plot is for conformation only Show when Signal is produced
    # if not (any(data['sum'][-5:] >= total_sum) or any(data['sum'][-5:] <= -total_sum)):
    #     continue

    # Making Plot for batter visualization
    plt.plot(data['Close'], label='Close Price')

    buy_indices = data.index[data['sum'] >= total_sum]
    sell_indices = data.index[data['sum'] <= -total_sum]
    plt.scatter(buy_indices, data['Close'][data['sum'] >= total_sum],
                marker='^', s=marker_sizes[data['sum'] >= total_sum], color='green', label='Buy signal', zorder=3)
    plt.scatter(sell_indices, data['Close'][data['sum'] <= -total_sum],
                marker='v', s=marker_sizes[data['sum'] <= -total_sum], color='red', label='Sell signal', zorder=3)

    # Add text labels for sum values
    # for i, index in enumerate(buy_indices):
    #     plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='bottom', fontsize=8)
    # for i, index in enumerate(sell_indices):
    #     plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='top', fontsize=8)

    # Add text labels for sum values and non-zero columns
    for i, index in enumerate(buy_indices):
        non_zero_cols = [(col, int(df.loc[index, col])) for col in df.columns if
                         df.loc[index, col] != 0]
        non_zero_cols.sort(key=lambda x: x[1])
        label = f"Sum: {data['sum'][index]}"
        for j, (col, value) in enumerate(non_zero_cols):
            # print(data['Close'][index])
            y_offset = (j + 1) * 10 if value > 0 else -(j + 1) * 10
            dot_color = 'g' if value > 0 else 'r'
            plt.plot(index, data['Close'][index] + y_offset, f'{dot_color}o', markersize=2)
            plt.text(index, data['Close'][index] + y_offset, f"{col}: {value}", color="#808080", ha='center', va='bottom', fontsize=8)
        plt.text(index, data['Close'][index], label, color="#808080", ha='center', va='bottom', fontsize=8)

    for i, index in enumerate(sell_indices):
        non_zero_cols = [(col, int(df.loc[index, col])) for col in df.columns if
                         df.loc[index, col] != 0]
        non_zero_cols.sort(key=lambda x: x[1])
        label = f"Sum: {data['sum'][index]}"
        for j, (col, value) in enumerate(non_zero_cols):
            y_offset = (j + 1) * 10 if value > 0 else -(j + 1) * 10
            dot_color = 'g' if value > 0 else 'r'
            plt.plot(index, data['Close'][index] + y_offset, f'{dot_color}o', markersize=2)
            plt.text(index, data['Close'][index] + y_offset, f"{col}: {value}", color="#808080", ha='center', va='top', fontsize=8)
        plt.text(index, data['Close'][index], label, color="#808080", ha='center', va='top', fontsize=8)

    # Instate of Figure write Symbol name
    plt.title(symbol)
    plt.legend()
    plt.show()


main()
