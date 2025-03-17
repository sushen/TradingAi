import talib
import matplotlib.pyplot as plt
from dataframe.dataframe import GetDataframe
import pandas as pd

class Rsi:
    def __init__(self):
        pass
    def create_rsi(self, df):
        data = pd.DataFrame({'price': df['Close']})
        # Calculate the RSI using TA-Lib
        data['rsi'] = talib.RSI(df['Close'], timeperiod=14)

        # Generate signals
        data['signal'] = 0
        data.loc[data['rsi'] > 70, 'signal'] = -100
        data.loc[data['rsi'] < 30, 'signal'] = 100

        return data

    def plot_rsi(self, data, ax=None, total_sum=100):
        if ax is None:
            fig, ax = plt.subplots()
        # ax.plot(data['price'], label='Close Price')
        ax.scatter(data.index[data['signal'] == total_sum], data['price'][data['signal'] == total_sum],
                    marker='^', s=20, color='green', zorder=3)
        ax.scatter(data.index[data['signal'] == -total_sum], data['price'][data['signal'] == -total_sum],
                    marker='v', s=20, color='red', zorder=3)
        # ax.set_title('RSI')
        ax.legend()
        # plt.show()
        return ax

if __name__ == '__main__':
    # Load data
    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    rsi = Rsi()
    data = rsi.create_rsi(data)
    print(data[600:])
    ax = rsi.plot_rsi(data)
    plt.show()