import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

import matplotlib.pyplot as plt
from database_ai.dataframe import GetDataframe
import pandas as pd


class MovingAverage:
    def __init__(self):
        pass

    def create_moving_average(self, df):
        data = pd.DataFrame({'price': df['Close'], 'CloseTime': df['CloseTime']})  # Add 'CloseTime'

        # Calculate moving averages
        data['ma_short'] = df['Close'].rolling(window=7).mean()
        data['ma_medium'] = df['Close'].rolling(window=25).mean()
        data['ma_long'] = df['Close'].rolling(window=90).mean()
        data['ma_golden'] = df['Close'].rolling(window=200).mean()

        # Step 1: Initialize the signal column to 0
        data['long_golden'] = 0
        data['short_medium'] = 0
        data['short_long'] = 0
        data['short_golden'] = 0
        data['medium_long'] = 0
        data['medium_golden'] = 0

        # Step 2: Use boolean masks to compare ma_long with ma_golden
        ma_long_mask = data['ma_long'] > data['ma_golden']
        ma_golden_mask = data['ma_long'] < data['ma_golden']
        ma_long_shifted = data['ma_long'].shift(1)
        ma_golden_shifted = data['ma_golden'].shift(1)
        ma_long_post = data['ma_long'].shift(-1)
        ma_golden_post = data['ma_golden'].shift(-1)

        data.loc[(ma_long_shifted < ma_golden_shifted) &
                 (ma_long_post > ma_golden_post), 'long_golden'] = 100
        data.loc[(ma_long_shifted > ma_golden_shifted) &
                 (ma_long_post < ma_golden_post), 'long_golden'] = -100

        ma_short_mask = data['ma_short'] > data['ma_medium']
        ma_medium_mask = data['ma_short'] < data['ma_medium']
        ma_short_shifted = data['ma_short'].shift(1)
        ma_medium_shifted = data['ma_medium'].shift(1)
        ma_short_post = data['ma_short'].shift(-1)
        ma_medium_post = data['ma_medium'].shift(-1)

        data.loc[(ma_short_shifted < ma_medium_shifted) &
                 (ma_short_post > ma_medium_post), 'short_medium'] = 100
        data.loc[(ma_short_shifted > ma_medium_shifted) &
                 (ma_short_post < ma_medium_post), 'short_medium'] = -100

        ma_short_mask = data['ma_short'] > data['ma_long']
        ma_long_mask = data['ma_short'] < data['ma_long']
        ma_short_shifted = data['ma_short'].shift(1)
        ma_long_shifted = data['ma_long'].shift(1)
        ma_short_post = data['ma_short'].shift(-1)
        ma_long_post = data['ma_long'].shift(-1)

        data.loc[(ma_short_shifted < ma_long_shifted) &
                 (ma_short_post > ma_long_post), 'short_long'] = 100
        data.loc[(ma_short_shifted > ma_long_shifted) &
                 (ma_short_post < ma_long_post), 'short_long'] = -100

        ma_short_mask = data['ma_short'] > data['ma_golden']
        ma_golden_mask = data['ma_short'] < data['ma_golden']
        ma_short_shifted = data['ma_short'].shift(1)
        ma_golden_shifted = data['ma_golden'].shift(1)
        ma_short_post = data['ma_short'].shift(-1)
        ma_golden_post = data['ma_golden'].shift(-1)

        data.loc[(ma_short_shifted < ma_golden_shifted) &
                 (ma_short_post > ma_golden_post), 'short_golden'] = 100
        data.loc[(ma_short_shifted > ma_golden_shifted) &
                 (ma_short_post < ma_golden_post), 'short_golden'] = -100

        ma_medium_mask = data['ma_medium'] > data['ma_long']
        ma_long_mask = data['ma_medium'] < data['ma_long']
        ma_medium_shifted = data['ma_medium'].shift(1)
        ma_long_shifted = data['ma_long'].shift(1)
        ma_medium_post = data['ma_medium'].shift(-1)
        ma_long_post = data['ma_long'].shift(-1)

        data.loc[(ma_medium_shifted < ma_long_shifted) &
                 (ma_medium_post > ma_long_post), 'medium_long'] = 100
        data.loc[(ma_medium_shifted > ma_long_shifted) &
                 (ma_medium_post < ma_long_post), 'medium_long'] = -100

        ma_medium_mask = data['ma_medium'] > data['ma_golden']
        ma_golden_mask = data['ma_medium'] < data['ma_golden']
        ma_medium_shifted = data['ma_medium'].shift(1)
        ma_golden_shifted = data['ma_golden'].shift(1)
        ma_medium_post = data['ma_medium'].shift(-1)
        ma_golden_post = data['ma_golden'].shift(-1)

        data.loc[(ma_medium_shifted < ma_golden_shifted) &
                 (ma_medium_post > ma_golden_post), 'medium_golden'] = 100
        data.loc[(ma_medium_shifted > ma_golden_shifted) &
                 (ma_medium_post < ma_golden_post), 'medium_golden'] = -100

        # identify where there are two consecutive values of 100 or -100
        mask = ((data['long_golden'].shift(1) == 100) & (data['long_golden'] == 100)) | (
                (data['long_golden'].shift(1) == -100) & (data['long_golden'] == -100))
        data.loc[mask, 'long_golden'] = 0

        mask = ((data['short_medium'].shift(1) == 100) & (data['short_medium'] == 100)) | (
                (data['short_medium'].shift(1) == -100) & (data['short_medium'] == -100))
        data.loc[mask, 'short_medium'] = 0

        mask = ((data['short_long'].shift(1) == 100) & (data['short_long'] == 100)) | (
                (data['short_long'].shift(1) == -100) & (data['short_long'] == -100))
        data.loc[mask, 'short_long'] = 0

        mask = ((data['short_golden'].shift(1) == 100) & (data['short_golden'] == 100)) | (
                (data['short_golden'].shift(1) == -100) & (data['short_golden'] == -100))
        data.loc[mask, 'short_golden'] = 0

        mask = ((data['medium_long'].shift(1) == 100) & (data['medium_long'] == 100)) | (
                (data['medium_long'].shift(1) == -100) & (data['medium_long'] == -100))
        data.loc[mask, 'medium_long'] = 0

        mask = ((data['medium_golden'].shift(1) == 100) & (data['medium_golden'] == 100)) | (
                (data['medium_golden'].shift(1) == -100) & (data['medium_golden'] == -100))
        data.loc[mask, 'medium_golden'] = 0

        # data['sum'] = data['signal1'] + data['signal2'] + data['signal3'] + data['signal4'] + data['signal5'] + data['signal6']
        return data

    def plot_moving_average(self, data, ax=None, total_sum=100):
        if ax is None:
            fig, ax = plt.subplots()
        # Plot moving averages
        ax.plot(data['ma_short'], label='Short-term moving average')
        ax.plot(data['ma_medium'], label='Medium-term moving average')
        ax.plot(data['ma_long'], label='Long-term moving average')
        ax.plot(data['ma_golden'], label='Golden-term moving average', color='yellow')

        ax.scatter(data.index[data['long_golden'] == total_sum], data['ma_golden'][data['long_golden'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['long_golden'] == -total_sum], data['ma_golden'][data['long_golden'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['short_medium'] == total_sum], data['ma_medium'][data['short_medium'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['short_medium'] == -total_sum], data['ma_medium'][data['short_medium'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['short_long'] == total_sum], data['ma_long'][data['short_long'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['short_long'] == -total_sum], data['ma_long'][data['short_long'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['short_golden'] == total_sum], data['ma_golden'][data['short_golden'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['short_golden'] == -total_sum], data['ma_golden'][data['short_golden'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['medium_long'] == total_sum], data['ma_long'][data['medium_long'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['medium_long'] == -total_sum], data['ma_long'][data['medium_long'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['medium_golden'] == total_sum], data['ma_golden'][data['medium_golden'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['medium_golden'] == -total_sum], data['ma_golden'][data['medium_golden'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)

        # ax.set_title('Moving Average')
        ax.legend()
        # plt.show()
        return ax


if __name__ == "__main__":
    from api_callling.api_calling import APICall

    api = APICall()
    from database_ai.dataframe import GetDataframe
    data = GetDataframe(api).get_minute_data('BTCUSDT', 1, 1000)
    print(data)
    ma = MovingAverage()
    data = ma.create_moving_average(data)
    print(data[['long_golden', 'short_medium', 'short_long', 'short_golden', 'medium_long', 'medium_golden']][600:])
    ax = ma.plot_moving_average(data)

    plt.show()
