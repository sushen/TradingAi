import matplotlib.pyplot as plt

from database.dataframe import GetDataframe

# Load data
data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
print(data)

# Calculate moving averages
data['ma_short'] = data['Close'].rolling(window=7).mean()
data['ma_long'] = data['Close'].rolling(window=90).mean()

# Plot moving averages
plt.plot(data['ma_short'], label='Short-term moving average')
plt.plot(data['ma_long'], label='Long-term moving average')
plt.legend()
plt.show()

# Generate signals
data['signal'] = 0
data.loc[data['ma_short'] > data['ma_long'], 'signal'] = 100
data.loc[data['ma_short'] < data['ma_long'], 'signal'] = -100

# Plot signals
plt.plot(data['signal'], label='Trading signal')
plt.legend()
plt.show()