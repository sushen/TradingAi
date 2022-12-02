import sqlite3

import pandas as pd
import talib
import matplotlib as mlt

# connection = sqlite3.connect("cripto.db")
# cur = connection.cursor()
# # database_data = cur.execute("select CloseTime from asset order by CloseTime desc limit 1").fetchall()
# database_data = cur.execute("select Open, High, Low, Close, VolumeBTC, CloseTime from asset order by CloseTime desc limit 5").fetchall()
# connection.commit()
# cur.close()
# print(database_data)
from dataframe import GetDataframe

symbol = "BTCBUSD"

df = GetDataframe().get_minute_data(symbol, 1, 100)
print(df)

# print(input("Stop:"))


def all_candle_list():
    all_candle = []
    for attr in dir(talib):
        if attr[:3] == "CDL":
            all_candle.append(attr)
    # print(all_candle)
    return all_candle


# for candle in all_candle_list():
#     print(candle)
    # result = (talib.candle)(df['Open'], df['High'], df['Low'], df['Close'])
    # print(result)

# df = df.head(5)

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
