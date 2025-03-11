import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

import talib
import matplotlib.pyplot as plt
from database_ai.dataframe import GetDataframe
import pandas as pd


class Rsi:
    def __init__(self):
        pass

    def create_rsi(self, df):
        # Check if 'CloseTime' exists in the data
        if 'CloseTime' not in df.columns:
            raise KeyError("'CloseTime' column is missing in the input data.")

        # Extract the 'CloseTime' column and convert it to datetime
        time_column = df['CloseTime']
        df['CloseTime'] = pd.to_datetime(time_column, unit='ms')  # Convert to datetime

        # Include both 'Close' and 'CloseTime' in the resulting DataFrame
        data = pd.DataFrame({'price': df['Close'], 'CloseTime': df['CloseTime']})

        # Calculate RSI using TA-Lib
        data['rsi'] = talib.RSI(df['Close'], timeperiod=14)

        # Generate signals based on RSI values
        data['signal'] = 0
        data.loc[data['rsi'] > 70, 'signal'] = -100  # Sell signal
        data.loc[data['rsi'] < 30, 'signal'] = 100  # Buy signal

        # Ensure that 'CloseTime' is correctly set as datetime64[ns]
        data = data.astype({'CloseTime': 'datetime64[ns]'})

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
    from api_callling.api_calling import APICall
    api = APICall()
    from database_ai.dataframe import GetDataframe
    data = GetDataframe(api).get_minute_data('BTCUSDT', 1, 1000)
    print(data)
    rsi = Rsi()
    data = rsi.create_rsi(data)
    print(data[600:])
    ax = rsi.plot_rsi(data)
    plt.show()
