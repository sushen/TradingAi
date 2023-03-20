import talib

import matplotlib.pyplot as plt

from dataframe import GetDataframe

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
# print(data)
prices = data['Close']


# Calculate the Bollinger Bands using TA-Lib
upperband, middleband, lowerband = talib.BBANDS(data['Close'], timeperiod=9, nbdevup=2, nbdevdn=2, matype=0)

print(upperband)
print(middleband)
print(lowerband)

# Initialize empty lists to store the signals
buy_signals = []
sell_signals = []

# Iterate through the prices and generate the signals
for i in range(len(prices)):
    if prices[i] < lowerband[i]:
        buy_signals.append(1)
        sell_signals.append(0)
    elif prices[i] > upperband[i]:
        buy_signals.append(0)
        sell_signals.append(1)
    else:
        buy_signals.append(0)
        sell_signals.append(0)

print(buy_signals)
print(sell_signals)

# Create a figure and axis
fig, ax = plt.subplots()

# Plot the prices, Bollinger Bands, and signals
ax.plot(prices, label='Prices')
ax.plot(upperband, label='Upper Band')
ax.plot(middleband, label='Middle Band')
ax.plot(lowerband, label='Lower Band')
ax.plot(buy_signals, '^', markersize=10, color='g', label='Buy')
ax.plot(sell_signals, 'v', markersize=10, color='r', label='Sell')

# Add a legend and show the plot
ax.legend()
plt.show()