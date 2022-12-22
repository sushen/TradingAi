import pandas as pd
import matplotlib.pyplot as plt

from dataframe import GetDataframe


import talib

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
print(data)

# Calculate SuperTrend
data['supertrend'] = talib.STOCHF(data['High'], data['Low'], data['Close'], fastk_period=10, fastd_period=3)

# Plot SuperTrend
plt.plot(data['supertrend'], label='Supertrend')
plt.legend()
plt.show()