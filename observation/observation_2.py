"""
To Make A plot This:
Script is running for 14 Minutes.

"""
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
    import time
    start_time = time.time()
    print("Script Start :", time.ctime())


    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    total_sum = 1000
    lookback = 1440*30*12*4
    # TODO: I need to remove 1 and 3 , I believe by doing that I will get more proper signal
    times = [1, 3, 5, 15, 30, 60, 4*60, 24*60, 7*24*60]  # Time periods

    # Initialize a variable to store the sum
    total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
    # connection = sqlite3.connect("C:\\Users\\user\\PycharmProjects\\TradingAiDevlopment\\database\\btcusdt_crypto_4years.db")
    # connection = sqlite3.connect("C:\\Users\\user\\PycharmProjects\\TradingAiDevlopment\\database\\big_crypto_4years.db")
    # connection = sqlite3.connect("C:\\Users\\user\\PycharmProjects\\TradingAiVersion4\\database\\big_crypto_4years.db")
    connection = sqlite3.connect("C:\\Users\\user\\PycharmProjects\\TradingAiVersion4\\database_small\\small_crypto.db")
    # connection = sqlite3.connect("../database/big_data.db")
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

    # Time Counting
    import time
    end_time = time.time()
    print("End Time: ", end_time)
    print("Script is running for " + str(int((end_time - start_time) / 60)) + " Minutes.")

    plt.title(symbol)
    plt.legend()
    plt.grid(True)
    plt.show()


# 38 symbols :
# ['BTCBUSD', 'ETHBUSD', 'BNBBUSD', 'ADABUSD', 'XRPBUSD', 'DOGEBUSD', 'SOLBUSD', 'FTTBUSD', 'AVAXBUSD', 'NEARBUSD', 'GMTBUSD', 'APEBUSD',
# 'GALBUSD', 'FTMBUSD', 'DODOBUSD', 'ANCBUSD', 'GALABUSD', 'TRXBUSD', '1000LUNCBUSD', 'DOTBUSD', 'TLMBUSD', 'WAVESBUSD', 'LINKBUSD',
# 'SANDBUSD', 'LTCBUSD', 'MATICBUSD', 'CVXBUSD', 'FILBUSD', '1000SHIBBUSD', 'LEVERBUSD', 'ETCBUSD', 'LDOBUSD', 'UNIBUSD', 'AUCTIONBUSD',
# 'AMBBUSD', 'PHBBUSD', 'APTBUSD', 'AGIXBUSD']

main("BTCUSDT")

# from database.exchange_info import BinanceExchange
#
# p_symbols = BinanceExchange()
# all_symbols_payers = p_symbols.get_specific_symbols()
# print(f"{len(all_symbols_payers)} symbols : {all_symbols_payers}")
#
# for index, symbol in enumerate(all_symbols_payers):
#     print(index + 1, symbol)
#     main(symbol)
