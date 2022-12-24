import talib

import matplotlib.pyplot as plt

from dataframe import GetDataframe

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
# print(data)

# Calculate the MACD using TA-Lib
macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

print(macd)
print(macdsignal)
print(macdhist)
