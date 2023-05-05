import time

import numpy as np
from database.dataframe import GetDataframe
import matplotlib.pyplot as plt
from indicator.indicators import CreateIndicators
from get_symbol.find_symbols import FindSymbols


def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    from api_callling.api_calling import APICall

    ticker_info = pd.DataFrame(APICall.client.get_ticker())
    # print(ticker_info)
    fs = FindSymbols()
    busd_symbole = fs.get_all_symbols("BUSD", ticker_info)
    # print(busd_symbole['symbol'])
    print(len(busd_symbole['symbol']))
    # print(input("....:"))

    for symbol in busd_symbole['symbol']:
        # print(symbol)
        # print(input("....:"))

        data = GetDataframe().get_minute_data(f'{symbol}', 1, 202)
        # print(data)
        ci = CreateIndicators(data)
        # print("All Indicators: ")
        df = ci.create_all_indicators()
        # print(df)
        data['sum'] = df.sum(axis=1)

        # print(data)

        marker_sizes = np.abs(data['sum']) / 10
        # Making Plot for batter visualization
        plt.plot(data['Close'], label='Close Price')

        # Add Buy and Sell signals
        total_sum = 800

        buy_indices = data.index[data['sum'] >= total_sum]
        sell_indices = data.index[data['sum'] <= -total_sum]
        plt.scatter(buy_indices, data['Close'][data['sum'] >= total_sum],
                    marker='^', s=marker_sizes[data['sum'] >= total_sum], color='green', label='Buy signal', zorder=3)
        plt.scatter(sell_indices, data['Close'][data['sum'] <= -total_sum],
                    marker='v', s=marker_sizes[data['sum'] <= -total_sum], color='red', label='Sell signal', zorder=3)

        plt.get_current_fig_manager().set_window_title(f'{symbol} Signal')
        # TODO : Plot is for conformation only Show when Signal is produced
        # Add text labels for sum values
        for i, index in enumerate(buy_indices):
            if df.index.get_loc(index) >= len(df)-5:
                non_zero_cols = [col for col in df.columns if df.loc[index, col] != 0]
                label = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(non_zero_cols)}"
                print(label)
            plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='bottom', fontsize=8)
        for i, index in enumerate(sell_indices):
            if df.index.get_loc(index) >= len(df)-5:
                non_zero_cols = [col for col in df.columns if df.loc[index, col] != 0]
                label = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(non_zero_cols)}"
                print(label)
            plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='top', fontsize=8)

        # TODO : Instate of Figure write Symbol name
        plt.legend()
        plt.show()
        time.sleep(4)
        plt.close()


main()
