import talib
import matplotlib.pyplot as plt
from database.dataframe import GetDataframe

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
# print(data)

# Calculate the MACD using TA-Lib
macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

data['macd'] = macd
data['macdsignal'] = macdsignal

data['signal'] = 0
data['signal'][data['macd'] > data['macdsignal']] = 100
data['signal'][data['macd'] < data['macdsignal']] = -100

data['new_signal'] = 0

# set the first non-duplicate value to new_col
prev_val = data['signal'].iloc[0]
data['new_signal'].iloc[0] = prev_val

# loop through the remaining rows and set the value of new_col
for i in range(1, len(data)):
    if data['signal'].iloc[i] == prev_val:
        data['new_signal'].iloc[i] = 0
    else:
        prev_val = data['signal'].iloc[i]
        data['new_signal'].iloc[i] = prev_val

print(data[['macd', 'macdsignal', 'signal', 'new_signal']][600:])

plt.plot(data['macd'], label='macd', color='blue')
plt.plot(data['macdsignal'], label='macdsignal', color='orange')

plt.scatter(data.index[data['new_signal'] == 100], data['macd'][data['new_signal'] == 100],
            marker='^', s=20, color='green', label='Buy signal', zorder=3)
plt.scatter(data.index[data['new_signal'] == -100], data['macd'][data['new_signal'] == -100],
            marker='v', s=20, color='red', label='Sell signal', zorder=3)

plt.legend(loc='upper left')
plt.show()



