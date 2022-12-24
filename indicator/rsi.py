import talib
import matplotlib.pyplot as plt

from dataframe import GetDataframe

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
print(data)
# Calculate the RSI using TA-Lib
rsi = talib.RSI(data['Close'], timeperiod=14)

print(rsi)

plt.plot(rsi, label='Trading signal')
plt.legend()
plt.show()