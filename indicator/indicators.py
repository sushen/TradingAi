import talib
import pandas as pd
from moving_average_signal import MovingAverage
from bollinger_bands import BollingerBand
from macd import Macd
from rsi import Rsi
from super_trend import SuperTrend
from candle_pattern import MakePattern

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
        return df['sum']

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

        df = pd.DataFrame({'bollinger_band': bd,
                           'moving_average': ma,
                           'macd': macd,
                           'rsi': rsi,
                           'super_trend': st})
        df = df.add(cp, fill_value=0)
        df = df.astype(int)
        return df

if __name__ == "__main__":
    from database.dataframe import GetDataframe
    import matplotlib.pyplot as plt
    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    ci = CreateIndicators(data)
    print("All Indicators: ")
    df = ci.create_all_indicators()
    print(df)
    data['sum'] = df.sum(axis=1)

    print(data)

    # Making Plot for batter visualization
    plt.plot(data['Close'], label='Close Price')
    plt.scatter(data.index[data['sum'] >= 100], data['Close'][data['sum'] >= 100],
                marker='^', s=20, color='green', label='Buy signal', zorder=3)
    plt.scatter(data.index[data['sum'] <= -100], data['Close'][data['sum'] <= -100],
                marker='v', s=20, color='red', label='Sell signal', zorder=3)
    plt.legend()
    plt.show()
