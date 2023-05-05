import talib
import matplotlib.pyplot as plt
from database.dataframe import GetDataframe

class Rsi:
    def __init__(self):
        pass
    def create_rsi(self, data):
        # Calculate the RSI using TA-Lib
        data['rsi'] = talib.RSI(data['Close'], timeperiod=14)

        # Generate signals
        data['signal'] = 0
        data.loc[data['rsi'] > 70, 'signal'] = -100
        data.loc[data['rsi'] < 30, 'signal'] = 100

        return data

    def plot_rsi(self, data):
        plt.plot(data['Close'], label='Close Price')
        plt.scatter(data.index[data['signal'] == 100], data['Close'][data['signal'] == 100],
                    marker='^', s=20, color='green', label='Buy signal', zorder=3)
        plt.scatter(data.index[data['signal'] == -100], data['Close'][data['signal'] == -100],
                    marker='v', s=20, color='red', label='Sell signal', zorder=3)
        plt.legend()
        plt.show()

if __name__ == '__main__':
    # Load data
    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    rsi = Rsi()
    data = rsi.create_rsi(data)
    print(data[600:])
    rsi.plot_rsi(data)