import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from indicator.moving_average_signal import MovingAverage
from indicator.bollinger_bands import BollingerBand
from indicator.macd import Macd
from indicator.rsi import Rsi
from indicator.super_trend import SuperTrend
from indicator.candle_pattern import MakePattern

class CreatePlot:
    def __init__(self, data):
        self.data = data

    def bollinger_band(self, ax=None):
        # It will show the plot for bollinger_band
        bb = BollingerBand()
        df = bb.create_bollinger_band(self.data)
        ax = bb.plot_bollinger_band(df, ax)
        return ax

    def moving_average(self, ax=None):
        # It will show the plot for moving_average
        ma = MovingAverage()
        df = ma.create_moving_average(self.data)
        ax = ma.plot_moving_average(df, ax)
        return ax

    def macd(self, ax=None):
        # It will show the plot for macd
        macd = Macd()
        df = macd.create_macd(self.data)
        ax = macd.plot_macd(df, ax)
        return ax

    def rsi(self, ax=None):
        # It will show the plot for rsi
        rsi = Rsi()
        df = rsi.create_rsi(self.data)
        ax = rsi.plot_rsi(df, ax)
        return ax

    def super_trend(self, ax=None):
        # It will show the plot for super_trend
        st = SuperTrend()
        df = st.create_super_trend(self.data)
        ax = st.plot_super_trend(df, ax)
        pass

    def candle_pattern(self, ax=None):
        # It will show the plot for candle_pattern
        pass

    def create_all_pattern(self, ax=None):
        # It will print all the pattern
        fig, axs = plt.subplots(nrows=2, ncols=3)
        ax1 = self.bollinger_band(axs[0, 0])
        ax2 = self.moving_average(axs[0, 1])
        ax3 = self.macd(axs[0, 2])
        ax4 = self.rsi(axs[1, 0])
        ax5 = self.super_trend(axs[1, 1])
        plt.show()

if __name__ == "__main__":
    from database.dataframe import GetDataframe

    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1440)
    cp = CreatePlot(data)
    cp.create_all_pattern()