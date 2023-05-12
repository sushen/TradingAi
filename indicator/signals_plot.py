import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from indicator.moving_average_signal import MovingAverage
from indicator.bollinger_bands import BollingerBand
from indicator.macd import Macd
from indicator.rsi import Rsi
from indicator.super_trend import SuperTrend
from indicator.candle_pattern import MakePattern


class CreatePlot:
    def __init__(self, data):
        self.data = data

    def bollinger_band(self, ax=None):
        # It will show the plot for bollinger_band
        bb = BollingerBand()
        df = bb.create_bollinger_band(self.data)
        ax = bb.plot_bollinger_band(df, ax)
        return ax

    def moving_average(self, ax=None):
        # It will show the plot for moving_average
        ma = MovingAverage()
        df = ma.create_moving_average(self.data)
        ax = ma.plot_moving_average(df, ax)
        return ax

    def macd(self, ax=None):
        # It will show the plot for macd
        macd = Macd()
        df = macd.create_macd(self.data)
        ax = macd.plot_macd(df, ax)
        return ax

    def rsi(self, ax=None):
        # It will show the plot for rsi
        rsi = Rsi()
        df = rsi.create_rsi(self.data)
        ax = rsi.plot_rsi(df, ax)
        return ax

    def super_trend(self, ax=None):
        # It will show the plot for super_trend
        st = SuperTrend()
        df = st.create_super_trend(self.data)
        ax = st.plot_super_trend(df, ax)
        return ax

    def candle_pattern(self, ax=None):
        # It will show the plot for candle_pattern
        pass

    def create_all_pattern(self, ax=None):
        # Create a dictionary to store the checkbox status
        plot_visibility = {
            "Bollinger Band": True,
            "Moving Average": True,
            "MACD": True,
            "RSI": True,
            "Super Trend": True
        }

        # Create a function to handle checkbox changes
        def update_plot_visibility(label):
            plot_visibility[label] = not plot_visibility[label]
            self.update_plots(axs, plot_visibility)

        fig, axs = plt.subplots()

        # Create checkboxes for each plot
        checkboxes = {}
        for i, (label, _) in enumerate(plot_visibility.items()):
            checkbox_ax = plt.axes([0.02, 0.9 - i * 0.1, 0.1, 0.1], facecolor='lightgoldenrodyellow')
            checkboxes[label] = CheckButtons(checkbox_ax, [label], [True])
            checkboxes[label].on_clicked(lambda _, l=label: update_plot_visibility(l))

        self.update_plots(axs, plot_visibility)

        plt.show()

    def update_plots(self, axs, plot_visibility):
        axs.clear()
        if plot_visibility["Bollinger Band"]:
            self.bollinger_band(axs)
        if plot_visibility["Moving Average"]:
            self.moving_average(axs)
        if plot_visibility["MACD"]:
            self.macd(axs)
        if plot_visibility["RSI"]:
            self.rsi(axs)
        if plot_visibility["Super Trend"]:
            self.super_trend(axs)
        plt.draw()


if __name__ == "__main__":
    from database.dataframe import GetDataframe

    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1440)
    cp = CreatePlot(data)
    cp.create_all_pattern()