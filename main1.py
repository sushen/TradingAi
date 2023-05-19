import time

import numpy as np
from database.dataframe import GetDataframe
import matplotlib.pyplot as plt
from indicator.indicators import CreateIndicators
from get_symbol.find_symbols import FindSymbols
import binance
from database.exchange_info import BinanceExchange
from datetime import datetime
from email_option.sending_mail import MailSender

sender = MailSender()
sender.login()

from googlesheet.connection import Connection
ws = Connection().connect_worksheet("tracker2")


def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    from api_callling.api_calling import APICall

    # ticker_info = pd.DataFrame(APICall.client.get_ticker())
    # print(ticker_info)

    # fs = FindSymbols()
    # busd_symbole = fs.get_all_symbols("BUSD", ticker_info)
    # print(busd_symbole['symbol'])
    # print(len(busd_symbole['symbol']))
    p_symbols = BinanceExchange()
    all_symbols_payers = p_symbols.get_specific_symbols()
    print(all_symbols_payers)
    print(len(all_symbols_payers))
    # print(input("....:"))

    # for symbol in all_symbols_payers:
    for index, symbol in enumerate(all_symbols_payers):
        print(index, symbol)

        # print(input("....:"))
        # TODO: Call Data Form Database

        try:
            data = GetDataframe().get_minute_data(f'{symbol}', 3, 202)
        except binance.exceptions.BinanceAPIException as e:
            print(f"Binance API exception: {e}")
            continue
        if data is None:
            continue
        # print(data)
        ci = CreateIndicators(data)
        # print("All Indicators: ")
        df = ci.create_all_indicators()
        # print(df)
        data['sum'] = df.sum(axis=1)

        # print(data)

        marker_sizes = np.abs(data['sum']) / 10
        # Add Buy and Sell signals
        total_sum = 800

        # Plot is for conformation only Show when Signal is produced
        if not (any(data['sum'][-5:] >= total_sum) or any(data['sum'][-5:] <= -total_sum)):
            continue

        # Making Plot for batter visualization
        # plt.plot(data['Close'], label='Close Price')
        buy_indices = data.index[data['sum'] >= total_sum]
        sell_indices = data.index[data['sum'] <= -total_sum]
        # plt.scatter(buy_indices, data['Close'][data['sum'] >= total_sum],
        #             marker='^', s=marker_sizes[data['sum'] >= total_sum], color='green', label='Buy signal', zorder=3)
        # plt.scatter(sell_indices, data['Close'][data['sum'] <= -total_sum],
        #             marker='v', s=marker_sizes[data['sum'] <= -total_sum], color='red', label='Sell signal', zorder=3)
        # plt.get_current_fig_manager().set_window_title(f'{symbol} Signal')

        # Add Google sheet to see the signal later
        # Email for get signal when we run it in the cloud

        # Add text labels for sum values
        for i, index in enumerate(buy_indices):
            if df.index.get_loc(index) >= len(df) - 5:
                p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
                p = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(p_cols)}"

                # Email Sending

                print("The Bullish sound")
                subject = symbol + " Bullish"
                Body = f"Bullish signal for {symbol} symbol.\nTotal signal value: {data['sum'][index]}." \
                       f"\n{p}."
                sender.send_mail("zihad.bscincse@gmail.com", subject, Body)
                sender.send_mail("tradingaitalib@gmail.com", subject, Body)

                body = [str(datetime.now()), symbol, int(data['sum'][index]), p]
                ws.append_row(body)

                print(p)
            # plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='bottom', fontsize=8)
        for i, index in enumerate(sell_indices):
            if df.index.get_loc(index) >= len(df) - 5:
                p_cols = [col + f"({str(df.loc[index, col])})" for col in df.columns if df.loc[index, col] != 0]
                p = f"Sum: {data['sum'][index]}  Non-zero indicators: {', '.join(p_cols)}"

                # Email Sending

                print("The Bearish sound")
                subject = symbol + " Bearish"
                Body = f"Bearish signal for {symbol} symbol.\nTotal signal value: {data['sum'][index]}." \
                       f"\n{p}."
                sender.send_mail("zihad.bscincse@gmail.com", subject, Body)
                sender.send_mail("tradingaitalib@gmail.com", subject, Body)

                body = [str(datetime.now()), symbol, int(data['sum'][index]), p]
                ws.append_row(body)

                print(p)
            # plt.text(index, data['Close'][index], str(data['sum'][index]), ha='center', va='top', fontsize=8)

        # Instate of Figure write Symbol name
        # plt.title(symbol)
        # plt.legend()
        # plt.show()
        # time.sleep(4)
        # plt.close()


while True:
    time.sleep(3)
    try:
        main()
    except:
        main()
        time.sleep(61)
        print("Testing")
