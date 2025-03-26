"""
Fibonacci Retracement Strategy:
https://youtu.be/nYKpik-o8zI?si=ZZDomb4nlfIFW09U
"""
import os
import sys
# Ensure the correct module path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pandas as pd
import matplotlib.pyplot as plt
import talib  # Technical analysis library


from api_callling.api_calling import APICall
from dataframe.dataframe import GetDataframe


class FibonacciRetracement:
    def __init__(self):
        pass

    def calculate_fibonacci(self, data):
        prices = data['Close']

        # Get max and min prices
        max_price = prices.max()
        min_price = prices.min()

        # Calculate Fibonacci levels
        difference = max_price - min_price
        first_level = max_price - 0.236 * difference
        second_level = max_price - 0.382 * difference
        third_level = max_price - 0.618 * difference

        return first_level, second_level, third_level, max_price, min_price

    def generate_signals(self, data, first_level, second_level, third_level):
        prices = data['Close']
        rsi = talib.RSI(prices, timeperiod=14)  # RSI calculation
        buy_signals = []
        sell_signals = []

        for i in range(len(prices)):
            # Buy signal: Price below 23.6% Fibonacci AND RSI < 30 (oversold) AND price starts increasing
            if prices[i] < first_level and rsi[i] < 30 and (i == 0 or prices[i] > prices[i-1]):
                buy_signals.append(100)
                sell_signals.append(0)

            # Sell signal: Price above 61.8% Fibonacci AND RSI > 70 (overbought) AND price starts decreasing
            elif prices[i] > third_level and rsi[i] > 70 and (i == 0 or prices[i] < prices[i-1]):
                buy_signals.append(0)
                sell_signals.append(-100)

            else:
                buy_signals.append(0)
                sell_signals.append(0)

        signal = [buy_signals[i] + sell_signals[i] for i in range(len(buy_signals))]
        data['buy_signals'] = buy_signals
        data['sell_signals'] = sell_signals
        data['signal'] = signal
        return data

    def plot_fibonacci(self, data, first_level, second_level, third_level, max_price, min_price, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        ax.plot(data['Close'], label='Prices', linewidth=2.0)
        ax.axhline(max_price, color='blue', linestyle='--', label='Max Price')
        ax.axhline(min_price, color='red', linestyle='--', label='Min Price')
        ax.axhline(first_level, color='green', linestyle='--', label='23.6% Fibonacci')
        ax.axhline(second_level, color='orange', linestyle='--', label='38.2% Fibonacci')
        ax.axhline(third_level, color='purple', linestyle='--', label='61.8% Fibonacci')

        ax.scatter(data.index[data['buy_signals'] == 100], data['Close'][data['buy_signals'] == 100],
                   marker='^', s=20, color='green', label='Buy signal', zorder=3)
        ax.scatter(data.index[data['sell_signals'] == -100], data['Close'][data['sell_signals'] == -100],
                   marker='v', s=20, color='red', label='Sell signal', zorder=3)

        ax.legend()
        return ax


if __name__ == '__main__':
    # Fetch data using API
    api = APICall()
    data = GetDataframe(api).get_minute_data('BTCUSDT', 30, 1440)  # Adjust parameters if needed

    fibonacci = FibonacciRetracement()
    first_level, second_level, third_level, max_price, min_price = fibonacci.calculate_fibonacci(data)
    data = fibonacci.generate_signals(data, first_level, second_level, third_level)

    ax = fibonacci.plot_fibonacci(data, first_level, second_level, third_level, max_price, min_price)
    # Title, legend, and grid
    plt.title(f"Fibonacci Retracement Strategy")
    plt.legend()
    plt.grid(True)
    plt.show()
