import talib
import numpy as np
import pandas as pd
from indicator.moving_average_signal import MovingAverage
from indicator.bollinger_bands import BollingerBand
from indicator.macd import Macd
from indicator.rsi import Rsi
from indicator.super_trend import SuperTrend
from indicator.candle_pattern import MakePattern


class CreateIndicators:
    def __init__(self, data):
        self.data = data

    def bollinger_band(self):
        bb = BollingerBand()
        df = bb.create_bollinger_band(self.data)
        return df['signal']

    def moving_average(self):
        # It will return the signal moving_average
        ma = MovingAverage()
        df = ma.create_moving_average(self.data)
        return df

    def macd(self):
        # It will return the signal macd
        macd = Macd()
        df = macd.create_macd(self.data)
        return df['new_signal']

    def rsi(self):
        # It will return the signal rsi
        rsi = Rsi()
        df = rsi.create_rsi(self.data)
        return df['signal']

    def super_trend(self):
        # It will return the signal super_trend
        st = SuperTrend()
        df = st.create_super_trend(self.data)
        return df['signal']

    def candle_pattern(self):
        # It will return the signal candle_pattern
        mp = MakePattern()
        pattern = mp.pattern(self.data)
        return pattern

    def create_all_indicators(self):
        bd = self.bollinger_band()
        ma = self.moving_average()
        macd = self.macd()
        rsi = self.rsi()
        st = self.super_trend()
        cp = self.candle_pattern()
        ma = ma[['long_golden', 'short_medium', 'short_long', 'short_golden', 'medium_long', 'medium_golden']]

        df = pd.DataFrame({'bollinger_band': bd,
                           'macd': macd,
                           'rsi': rsi,
                           'super_trend': st})
        df = df.add(ma, fill_value=0)
        df = df.add(cp, fill_value=0)
        df = df.astype(int)
        return df


if __name__ == "__main__":
    from database.dataframe import GetDataframe
    import matplotlib.pyplot as plt

    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1440)
    ci = CreateIndicators(data)
    print("All Indicators: ")
    df = ci.create_all_indicators()
    print(df)
    data['sum'] = df.sum(axis=1)

    print(data)

    marker_sizes = np.abs(data['sum']) / 10
    # Making Plot for batter visualization
    plt.plot(data['Close'], label='Close Price')

    # Add Buy and Sell signals
    total_sum = 500

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
            y_offset = (j + 1) * 10 if value > 0 else -(j + 1) * 10
            dot_color = 'g' if value > 0 else 'r'
            plt.plot(index, data['Close'][index] + y_offset, f'{dot_color}o', markersize=2)
            plt.text(index, data['Close'][index] + y_offset, f"{col}: {value}", ha='center', va='bottom', fontsize=8)
        plt.text(index, data['Close'][index], label, ha='center', va='bottom', fontsize=8)

    for i, index in enumerate(sell_indices):
        non_zero_cols = [(col, int(df.loc[index, col])) for col in df.columns if
                         df.loc[index, col] != 0]
        non_zero_cols.sort(key=lambda x: x[1])
        label = f"Sum: {data['sum'][index]}"
        for j, (col, value) in enumerate(non_zero_cols):
            y_offset = (j + 1) * 10 if value > 0 else -(j + 1) * 10
            dot_color = 'g' if value > 0 else 'r'
            plt.plot(index, data['Close'][index] + y_offset, f'{dot_color}o', markersize=2)
            plt.text(index, data['Close'][index] + y_offset, f"{col}: {value}", ha='center', va='top', fontsize=8)
        plt.text(index, data['Close'][index], label, ha='center', va='top', fontsize=8)

    plt.legend()
    plt.show()
