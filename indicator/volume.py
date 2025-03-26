import os
import sys
# Ensure the correct module path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import talib
import pandas as pd
import matplotlib.pyplot as plt

from api_callling.api_calling import APICall
from dataframe.dataframe import GetDataframe


class VolumeIndicator:
    def __init__(self):
        pass

    def create_volume_indicator(self, data, volume_window=20, volume_threshold=1.5):
        prices = data['Close']
        volume = data['VolumeUSDT']  # Volume data in USDT

        # Calculate the Moving Average of Volume (Volume_MA)
        volume_ma = volume.rolling(window=volume_window).mean()

        # Align the lengths by dropping the first 'volume_window' NaN values
        volume_ma = volume_ma.dropna()  # Drop NaN values
        prices = prices[volume_ma.index]  # Align prices with volume_ma after dropping NaNs
        volume = volume[volume_ma.index]  # Align volume with volume_ma after dropping NaNs

        # Initialize empty lists to store the signals
        buy_signals = []
        sell_signals = []

        for i in range(1, len(prices)):  # Starting from index 1 to avoid out-of-bounds errors
            # Buy Signal: Volume is greater than moving average by a threshold (Volume Spike) AND price is rising
            if volume[i] > volume_ma[i] * volume_threshold and prices[i] > prices[i - 1]:
                buy_signals.append(100)
                sell_signals.append(0)

            # Sell Signal: Volume is lower than moving average by a threshold AND price is falling
            elif volume[i] < volume_ma[i] * volume_threshold and prices[i] < prices[i - 1]:
                buy_signals.append(0)
                sell_signals.append(-100)

            else:
                buy_signals.append(0)
                sell_signals.append(0)

        # Create a signal column combining buy and sell signals
        signal = [buy_signals[i] + sell_signals[i] for i in range(len(buy_signals))]

        # Ensure the final data is correctly indexed
        data = pd.DataFrame({
            'prices': prices,
            'volume': volume,
            'volume_ma': volume_ma,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'signal': signal
        }, index=volume_ma.index)  # Use the volume_ma index to align the DataFrame

        return data

    def plot_volume_indicator(self, data, ax=None, total_sum=100):
        # Create a figure and axis
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 7))

        # Plot the prices and volume moving average
        ax.plot(data['prices'], label='Prices', linewidth=2.0)
        ax.plot(data['volume_ma'], label='Volume Moving Average', linestyle='--', linewidth=1.5, color='orange')

        # Plot buy and sell signals with reduced size and transparency
        ax.scatter(data.index[data['buy_signals'] == total_sum], data['prices'][data['buy_signals'] == total_sum],
                   marker='^', s=30, color='green', alpha=0.7, label='Buy signal', zorder=3)
        ax.scatter(data.index[data['sell_signals'] == -total_sum], data['prices'][data['sell_signals'] == -total_sum],
                   marker='v', s=30, color='red', alpha=0.7, label='Sell signal', zorder=3)

        # Add a legend and show the plot
        ax.legend()
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Price (USDT)', fontsize=12)
        ax.set_title('Price with Volume-Based Buy/Sell Signals', fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.5)
        return ax


if __name__ == '__main__':
    api = APICall()
    # Load data
    data = GetDataframe(api).get_minute_data('BTCUSDT', 1, 500)

    # Check for the correct columns
    print(data.columns)  # Ensure 'VolumeUSDT' and 'Close' columns are present

    # Initialize the VolumeIndicator class
    volume_indicator = VolumeIndicator()

    # Create volume indicator and signals
    data = volume_indicator.create_volume_indicator(data)

    # Print the data with generated signals
    print(data[5:])

    # Plot the volume indicator with buy/sell signals on the price chart
    ax = volume_indicator.plot_volume_indicator(data)
    plt.show()
