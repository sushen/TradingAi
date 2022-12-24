import pandas as pd
import matplotlib.pyplot as plt

from dataframe import GetDataframe


import talib

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
data = data.iloc[:, 0:4]
print(data)
# print(input(":"))
# Calculate SuperTrend
supertrend = talib.STOCHF(data['High'], data['Low'], data['Close'], fastk_period=10, fastd_period=3)
print(supertrend)

# Plot SuperTrend
plt.plot(supertrend, label='Supertrend')
plt.legend()
plt.show()