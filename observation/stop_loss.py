import sqlite3
import numpy as np
from database.db_dataframe import GetDbDataframe
import matplotlib.pyplot as plt
from datetime import timedelta


def main(symbol):
    import pandas as pd
    import time
    start_time = time.time()
    print("Start Time: ", start_time)
    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    total_sum = 1700
    lookback = 4*30*1440
    times = [1, 3, 5, 15, 30]  # Time periods[1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]

    # Initialize a variable to store the sum
    total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
    connection = sqlite3.connect("../database/big_crypto.db")
    db_frame = GetDbDataframe(connection)

    # Resample data for each time period and plot
    for t in times:
        resampled_data = db_frame.get_minute_data(symbol, t, lookback)
        df = db_frame.get_all_indicators(symbol, t, lookback)
        df.index = resampled_data.index
        resampled_data = resampled_data[~resampled_data.index.duplicated(keep='first')]
        df = df[~df.index.duplicated(keep='first')]
        resampled_data['sum'] = df.sum(axis=1)

        # Add the sum to the total sum
        total_sum_values = total_sum_values.add(resampled_data['sum'], fill_value=0)

    total_sum_values = total_sum_values.fillna(0).astype(np.int16)
    resampled_data = db_frame.get_minute_data(symbol, 1, lookback)
    resampled_data['sum'] = total_sum_values

    buy_indices = resampled_data.index[resampled_data['sum'] >= total_sum]
    sell_indices = resampled_data.index[resampled_data['sum'] <= -total_sum]

    ######### START PLOTTING #########
    marker_sizes = np.abs(resampled_data['sum']) / 10
    plt.plot(resampled_data['High'], label='High Price', linewidth=0.3, color='green')
    plt.plot(resampled_data['Low'], label='Low Price', linewidth=0.3, color='red')
    plt.plot(resampled_data['Close'], label='Close Price')
    plt.scatter(buy_indices, resampled_data['Close'][resampled_data['sum'] >= total_sum],
                marker='^', s=marker_sizes[resampled_data['sum'] >= total_sum], color='green',
                zorder=3)
    plt.scatter(sell_indices, resampled_data['Close'][resampled_data['sum'] <= -total_sum],
                marker='v', s=marker_sizes[resampled_data['sum'] <= -total_sum], color='red',
                zorder=3)
    ######### END PLOTTING #########

    stop_loss_df = pd.DataFrame(index=buy_indices, columns=['Close', '1st_HH', '1st_LL', '2nd_HH', 'max_profit'])
    for n, index in enumerate(buy_indices):

        # First HH
        high_values = resampled_data.loc[resampled_data.index > index][['High', 'Low']]
        hh_1 = resampled_data.loc[index]['High']
        hh_inx_1 = index
        for i, p in enumerate(high_values['High']):
            if i == 0:
                continue
            elif hh_1 < p:
                hh_1 = p
                hh_inx_1 = high_values.index[i]
                lst_inx = high_values.index[i]
            elif high_values.iloc[i]['Low'] < resampled_data.loc[index]['Close']:
                lst_inx = high_values.index[i]
                break
        # First LL
        low_values = resampled_data.loc[resampled_data.index > lst_inx][['High', 'Low']]
        ll_1 = resampled_data.loc[lst_inx]['Low']
        ll_inx_1 = lst_inx
        for i, p in enumerate(low_values['Low']):
            if i == 0:
                continue
            elif ll_1 > p:
                ll_1 = p
                ll_inx_1 = low_values.index[i]
                lst_inx = low_values.index[i]
            elif low_values.iloc[i]['High'] > resampled_data.loc[index]['Close']:
                lst_inx = low_values.index[i]
                break
        # Second HH
        high_values = resampled_data.loc[resampled_data.index > lst_inx][['High', 'Low']]
        hh_2 = resampled_data.loc[lst_inx]['High']
        hh_inx_2 = lst_inx
        for i, p in enumerate(high_values['High']):
            if i == 0:
                continue
            elif hh_2 < p:
                hh_2 = p
                hh_inx_2 = high_values.index[i]
            elif high_values.iloc[i]['Low'] < resampled_data.loc[index]['Close']:
                break
        max_profit = resampled_data.loc[index:index + timedelta(minutes=1440)]['Close'].max()
        stop_loss_df.loc[index] = [resampled_data['Close'][index], hh_1, ll_1, hh_2, max_profit]

        ######### START PLOTTING #########
        plt.text(index, resampled_data['Close'][index], f'{resampled_data["sum"][index]}({n})',
                 ha='center', va='bottom', fontsize=8)
        plt.text(hh_inx_1, resampled_data['High'][hh_inx_1], f'1st HH({n})', ha='center', va='bottom', fontsize=8,
                 color='blue')
        plt.text(ll_inx_1, resampled_data['Low'][ll_inx_1], f'1st LL({n})', ha='center', va='top', fontsize=8,
                 color='red')
        plt.text(hh_inx_2, resampled_data['High'][hh_inx_2], f'2nd HH({n})', ha='center', va='bottom', fontsize=8,
                 color='green')
        ######### END PLOTTING #########

    # Display the stop_loss_df
    stop_loss_df["tolerance"] = ((stop_loss_df['2nd_HH']-stop_loss_df['1st_LL'])/stop_loss_df['1st_LL'])*100
    print(stop_loss_df)
    average_stop_loss = stop_loss_df["tolerance"].mean()
    max_tolerance = stop_loss_df["tolerance"].max()
    min_tolerance = stop_loss_df["tolerance"].min()
    print()
    print("Average Stop Loss: ", format(average_stop_loss, ".2f"), "%")
    print("Max tolerance: ", format(max_tolerance, ".2f"), "%")
    print("Min tolerance: ", format(min_tolerance, ".2f"), "%")
    print()
    stop_loss_df["max_profit"] = (stop_loss_df["max_profit"]-(average_stop_loss/100)*stop_loss_df["max_profit"])
    stop_loss_df["max_profit_percentage"] = ((stop_loss_df['max_profit'] - stop_loss_df['Close']) / stop_loss_df['Close']) * 100
    average_max_profit = stop_loss_df["max_profit_percentage"].mean()
    max_profit = stop_loss_df["max_profit_percentage"].max()
    min_profit = stop_loss_df["max_profit_percentage"].min()
    print(f"Based on average stop loss we can gain:")
    print("Average profit: ", format(average_max_profit, ".2f"), "%")
    print("Max profit: ", format(max_profit, ".2f"), "%")
    print("Max loss: ", format(min_profit, ".2f"), "%")
    print()

    end_time = time.time()
    print("End Time: ", end_time)
    print("This Script is running for " + str(int((end_time - start_time) / 60)) + " Minutes.")

    ######### START PLOTTING #########
    plt.title(symbol)
    plt.legend()
    plt.grid(True)
    plt.show()
    ######### END PLOTTING #########


main("BTCBUSD")