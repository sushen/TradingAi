import pandas as pd
import talib
import matplotlib.pyplot as plt
from database.dataframe import GetDataframe

class Macd:
    def __init__(self):
        pass
    def create_macd(self, df):
        # Calculate the MACD using TA-Lib
        macd, macdsignal, macdhist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

        data = pd.DataFrame({'price' : df['Close']})

        data['macd'] = macd
        data['macdsignal'] = macdsignal
        data['signal'] = 0
        data['signal'][data['macd'] > data['macdsignal']] = 100
        data['signal'][data['macd'] < data['macdsignal']] = -100
        data['new_signal'] = 0

        # set the first non-duplicate value to new_col
        prev_val = data['signal'].iloc[0]
        data['new_signal'].iloc[0] = prev_val

        # loop through the remaining rows and set the value of new_col
        for i in range(1, len(data)):
            if data['signal'].iloc[i] == prev_val:
                data['new_signal'].iloc[i] = 0
            else:
                prev_val = data['signal'].iloc[i]
                data['new_signal'].iloc[i] = prev_val
        return data

    def plot_macd(self, data, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        ax.plot(data['macd'], label='macd', color='blue')
        ax.plot(data['macdsignal'], label='macdsignal', color='orange')

        ax.scatter(data.index[data['new_signal'] == 100], data['macd'][data['new_signal'] == 100],
                    marker='^', s=20, color='green', label='Buy signal', zorder=3)
        ax.scatter(data.index[data['new_signal'] == -100], data['macd'][data['new_signal'] == -100],
                    marker='v', s=20, color='red', label='Sell signal', zorder=3)

        ax.set_title('MACD')
        ax.legend(loc='upper left')
        return ax

if __name__ == "__main__":
    # Load data
    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    macd = Macd()
    data = macd.create_macd(data)
    print(data[['macd', 'macdsignal', 'signal', 'new_signal']][600:])
    ax = macd.plot_macd(data)
    plt.show()


