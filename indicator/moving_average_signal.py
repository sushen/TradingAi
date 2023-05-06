import matplotlib.pyplot as plt
from database.dataframe import GetDataframe
import pandas as pd


class MovingAverage:
    def __init__(self):
        pass

    def create_moving_average(self, df):
        data = pd.DataFrame({'price': df['Close']})
        # Calculate moving averages
        data['ma_short'] = df['Close'].rolling(window=7).mean()
        data['ma_medium'] = df['Close'].rolling(window=25).mean()
        data['ma_long'] = df['Close'].rolling(window=90).mean()
        data['ma_golden'] = df['Close'].rolling(window=200).mean()

        # Step 1: Initialize the signal column to 0
        data['signal1'] = 0
        data['signal2'] = 0
        data['signal3'] = 0
        data['signal4'] = 0
        data['signal5'] = 0
        data['signal6'] = 0

        # Step 2: Use boolean masks to compare ma_long with ma_golden
        ma_long_mask = data['ma_long'] > data['ma_golden']
        ma_golden_mask = data['ma_long'] < data['ma_golden']
        ma_long_shifted = data['ma_long'].shift(1)
        ma_golden_shifted = data['ma_golden'].shift(1)
        ma_long_post = data['ma_long'].shift(-1)
        ma_golden_post = data['ma_golden'].shift(-1)

        data.loc[(ma_long_shifted < ma_golden_shifted) &
                 (ma_long_post > ma_golden_post), 'signal1'] = 100
        data.loc[(ma_long_shifted > ma_golden_shifted) &
                 (ma_long_post < ma_golden_post), 'signal1'] = -100

        ma_short_mask = data['ma_short'] > data['ma_medium']
        ma_medium_mask = data['ma_short'] < data['ma_medium']
        ma_short_shifted = data['ma_short'].shift(1)
        ma_medium_shifted = data['ma_medium'].shift(1)
        ma_short_post = data['ma_short'].shift(-1)
        ma_medium_post = data['ma_medium'].shift(-1)

        data.loc[(ma_short_shifted < ma_medium_shifted) &
                 (ma_short_post > ma_medium_post), 'signal2'] = 100
        data.loc[(ma_short_shifted > ma_medium_shifted) &
                 (ma_short_post < ma_medium_post), 'signal2'] = -100

        ma_short_mask = data['ma_short'] > data['ma_long']
        ma_long_mask = data['ma_short'] < data['ma_long']
        ma_short_shifted = data['ma_short'].shift(1)
        ma_long_shifted = data['ma_long'].shift(1)
        ma_short_post = data['ma_short'].shift(-1)
        ma_long_post = data['ma_long'].shift(-1)

        data.loc[(ma_short_shifted < ma_long_shifted) &
                 (ma_short_post > ma_long_post), 'signal3'] = 100
        data.loc[(ma_short_shifted > ma_long_shifted) &
                 (ma_short_post < ma_long_post), 'signal3'] = -100

        ma_short_mask = data['ma_short'] > data['ma_golden']
        ma_golden_mask = data['ma_short'] < data['ma_golden']
        ma_short_shifted = data['ma_short'].shift(1)
        ma_golden_shifted = data['ma_golden'].shift(1)
        ma_short_post = data['ma_short'].shift(-1)
        ma_golden_post = data['ma_golden'].shift(-1)

        data.loc[(ma_short_shifted < ma_golden_shifted) &
                 (ma_short_post > ma_golden_post), 'signal4'] = 100
        data.loc[(ma_short_shifted > ma_golden_shifted) &
                 (ma_short_post < ma_golden_post), 'signal4'] = -100

        ma_medium_mask = data['ma_medium'] > data['ma_long']
        ma_long_mask = data['ma_medium'] < data['ma_long']
        ma_medium_shifted = data['ma_medium'].shift(1)
        ma_long_shifted = data['ma_long'].shift(1)
        ma_medium_post = data['ma_medium'].shift(-1)
        ma_long_post = data['ma_long'].shift(-1)

        data.loc[(ma_medium_shifted < ma_long_shifted) &
                 (ma_medium_post > ma_long_post), 'signal5'] = 100
        data.loc[(ma_medium_shifted > ma_long_shifted) &
                 (ma_medium_post < ma_long_post), 'signal5'] = -100

        ma_medium_mask = data['ma_medium'] > data['ma_golden']
        ma_golden_mask = data['ma_medium'] < data['ma_golden']
        ma_medium_shifted = data['ma_medium'].shift(1)
        ma_golden_shifted = data['ma_golden'].shift(1)
        ma_medium_post = data['ma_medium'].shift(-1)
        ma_golden_post = data['ma_golden'].shift(-1)

        data.loc[(ma_medium_shifted < ma_golden_shifted) &
                 (ma_medium_post > ma_golden_post), 'signal6'] = 100
        data.loc[(ma_medium_shifted > ma_golden_shifted) &
                 (ma_medium_post < ma_golden_post), 'signal6'] = -100

        # identify where there are two consecutive values of 100 or -100
        mask = ((data['signal1'].shift(1) == 100) & (data['signal1'] == 100)) | (
                (data['signal1'].shift(1) == -100) & (data['signal1'] == -100))
        data.loc[mask, 'signal1'] = 0
        mask = ((data['signal2'].shift(1) == 100) & (data['signal2'] == 100)) | (
                (data['signal2'].shift(1) == -100) & (data['signal2'] == -100))
        data.loc[mask, 'signal2'] = 0
        mask = ((data['signal3'].shift(1) == 100) & (data['signal3'] == 100)) | (
                (data['signal3'].shift(1) == -100) & (data['signal3'] == -100))
        data.loc[mask, 'signal3'] = 0
        mask = ((data['signal4'].shift(1) == 100) & (data['signal4'] == 100)) | (
                (data['signal4'].shift(1) == -100) & (data['signal4'] == -100))
        data.loc[mask, 'signal4'] = 0
        mask = ((data['signal5'].shift(1) == 100) & (data['signal5'] == 100)) | (
                (data['signal5'].shift(1) == -100) & (data['signal5'] == -100))
        data.loc[mask, 'signal5'] = 0
        mask = ((data['signal6'].shift(1) == 100) & (data['signal6'] == 100)) | (
                (data['signal6'].shift(1) == -100) & (data['signal6'] == -100))
        data.loc[mask, 'signal6'] = 0

        data['sum'] = data['signal1'] + data['signal2'] + data['signal3'] + data['signal4'] + data['signal5'] + data[
            'signal6']
        return data

    def plot_moving_average(self, data, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
        # Plot moving averages
        ax.plot(data['ma_short'], label='Short-term moving average')
        ax.plot(data['ma_medium'], label='Medium-term moving average')
        ax.plot(data['ma_long'], label='Long-term moving average')
        ax.plot(data['ma_golden'], label='Golden-term moving average', color='yellow')

        ax.scatter(data.index[data['signal1'] == 100], data['ma_golden'][data['signal1'] == 100],
                    marker='^', s=20, color='green', label='Buy signal', zorder=3)
        ax.scatter(data.index[data['signal1'] == -100], data['ma_golden'][data['signal1'] == -100],
                    marker='v', s=20, color='red', label='Sell signal', zorder=3)

        ax.scatter(data.index[data['signal2'] == 100], data['ma_medium'][data['signal2'] == 100],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['signal2'] == -100], data['ma_medium'][data['signal2'] == -100],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['signal3'] == 100], data['ma_long'][data['signal3'] == 100],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['signal3'] == -100], data['ma_long'][data['signal3'] == -100],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['signal4'] == 100], data['ma_golden'][data['signal4'] == 100],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['signal4'] == -100], data['ma_golden'][data['signal4'] == -100],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['signal5'] == 100], data['ma_long'][data['signal5'] == 100],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['signal5'] == -100], data['ma_long'][data['signal5'] == -100],
                    marker='v', s=20, color='red', zorder=3)

        ax.scatter(data.index[data['signal6'] == 100], data['ma_golden'][data['signal6'] == 100],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['signal6'] == -100], data['ma_golden'][data['signal6'] == -100],
                    marker='v', s=20, color='red', zorder=3)

        ax.set_title('Moving Average')
        ax.legend()
        # plt.show()
        return ax


if __name__ == "__main__":
    # Load data
    data = GetDataframe().get_minute_data('BNBBUSD', 1, 1000)
    print(data)
    ma = MovingAverage()
    data = ma.create_moving_average(data)
    print(data[['signal1', 'signal2', 'signal3', 'signal4', 'signal5', 'signal6', 'sum']][600:])
    ax = ma.plot_moving_average(data)
    plt.show()