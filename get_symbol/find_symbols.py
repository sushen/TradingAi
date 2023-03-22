# https://python-binance.readthedocs.io/en/latest/index.html


low_profit_con = ['BTCBUSD']
bad_coin = ['BUSDBKRW', 'KEEPBUSD', 'NUBUSD', 'STRATBUSD', 'RLCBUSD', 'SWRVBUSD', 'RAMPBUSD', 'ETHBULLBUSD', 'BOTBUSD',
            'GNOBUSD', 'BEARBUSD', 'BULLBUSD', 'AIONBUSD', 'BTTBUSD', 'XRPBEARBUSD', 'XRPBULLBUSD', 'RGTBUSD',
            'ETHBEARBUSD', 'NANOBUSD', 'BCHABUSD', 'HEGICBUSD', 'BTSBUSD', 'EOSBEARBUSD', 'COVERBUSD', 'EPSBUSD',
            'YFIIBUSD', 'EOSBULLBUSD', 'BUSDBVND', 'TRUBUSD', 'XEMBUSD', 'PAXBUSD', 'BUSDIDRT', 'FLMBUSD', 'BUSDNGN',
            'VTHOBUSD', 'BCHABCBUSD', 'USTBUSD', 'KMDBUSD', 'BNBBULLBUSD', 'LENDBUSD', 'REPBUSD', 'BUSDZAR', 'DAIBUSD',
            'BNBBEARBUSD', 'DCRBUSD', 'ANYBUSD', 'IRISBUSD', 'USDSBUSDS', 'ERDBUSD', 'PHBUSDC', 'BZRXBUSD', 'BKRWBUSD',
            'USDSBUSDT', 'BNBUSDS', 'WNXMBUSD']
faulty_coin = ['TORNBUSD']
unnecessary_keyword = ['UP', 'DOWN']
controversial_coin = ['SHIBUSDT']
unnecessary_payer = ['BNBUSDC', 'BNBUSDT']
fiat_currency = ['BUSDTRY', 'BUSDBRL', 'BUSDRON', 'BUSDPLN', 'BUSDUAH', 'CKBUSDT', 'BUSDRUB']

total_unnecessary_coin = bad_coin + faulty_coin + unnecessary_keyword + controversial_coin + low_profit_con + unnecessary_payer + fiat_currency

# print(total_unnecessary_coin)
# print(input("Stop"))


class FindSymbols:

    @staticmethod
    def get_all_symbols(currency_symbol, candle_info):
        all_bad_coin = total_unnecessary_coin
        busd_info = candle_info[candle_info.symbol.str.contains(currency_symbol)]
        non_leverage = busd_info[~busd_info['symbol'].isin(all_bad_coin)]
        non_leverage.priceChangePercent = non_leverage['priceChangePercent'].astype(float)
        non_leverage = non_leverage.sort_values(by='priceChangePercent', ascending=False)
        non_leverage = non_leverage.iloc[:, :4]
        # symbols = non_leverage
        symbols = non_leverage.loc[non_leverage['priceChangePercent'].astype(float) > 0]
        # print(f"{len(symbols)} symbol we are processing.")
        # print(symbols)
        # print(input("test pose:"))
        # return symbols.head(2)
        return symbols

# import pandas as pd
# pd.set_option('mode.chained_assignment', None)
# #
# # pd.set_option('display.max_rows', 500)
# # pd.set_option('display.max_columns', 500)
# # pd.set_option('display.width', 1000)
# #
# from api_callling.api_calling import APICall
# ticker_info = pd.DataFrame(APICall.client.get_ticker())
# # print(ticker_info)
# fs = FindSymbols()
# fs.get_all_symbols("BUSD", ticker_info)