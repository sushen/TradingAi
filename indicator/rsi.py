import talib
import matplotlib.pyplot as plt

from dataframe import GetDataframe

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
# print(data)

# Calculate the RSI using TA-Lib
data['rsi'] = talib.RSI(data['Close'], timeperiod=5)
# print(data['rsi'].to_string())

# Generate signals
data['signal'] = 0
data.loc[data['rsi'] > 70, 'signal'] = -100
data.loc[data['rsi'] < 30, 'signal'] = 100
# print(data['signal'].to_string())

plt.plot(data['signal'], label='Trading signal')
plt.legend()
plt.show()
