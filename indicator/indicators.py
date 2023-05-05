import talib
import pandas as pd
from moving_average_signal import MovingAverage
from bollinger_bands import BollingerBand
from macd import Macd
from rsi import Rsi

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
        pass

    def candle_pattern(self):
        # It will return the signal candle_pattern
        pass

