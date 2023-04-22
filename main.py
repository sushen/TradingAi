import sqlite3

import pandas as pd
import talib
import matplotlib as mlt


from dataframe import GetDataframe

symbol = "BTCBUSD"

df = GetDataframe().get_minute_data(symbol, 1, 100)
print(df)


def all_candle_list():
    all_candle = []
    for attr in dir(talib):
        if attr[:3] == "CDL":
            all_candle.append(attr)
    print(all_candle)
    return all_candle


#  We will make data like dummy data for the SQL data

results = []
cols = []
for attr in dir(talib):
    if attr[:3] == 'CDL':
        print(getattr(talib, attr))
        res = getattr(talib, attr)(df['Open'], df['High'], df['Low'], df['Close'])
        results.append(res)
        cols.append(attr)

patterns = pd.DataFrame(results).T
patterns.columns = cols
print(patterns)

all_pats = patterns.sum(axis=1)
print(all_pats)
all_pats.plot()



# TODO: after getting the 0, 100 and - 100 you will fid that to model with candle index what you already did with dummy data
#
# if __name__ == '__main__':
#     all_candle_list()


# TODO: create we will while loop that tell us every minutes the market
