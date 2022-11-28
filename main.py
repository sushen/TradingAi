import sqlite3

import talib

# connection = sqlite3.connect("cripto.db")
# cur = connection.cursor()
# # database_data = cur.execute("select CloseTime from asset order by CloseTime desc limit 1").fetchall()
# database_data = cur.execute("select Open, High, Low, Close, VolumeBTC, CloseTime from asset order by CloseTime desc limit 5").fetchall()
# connection.commit()
# cur.close()
# print(database_data)
from dataframe import GetDataframe

symbol = "BTCBUSD"

df = GetDataframe().get_minute_data(symbol, 1, 5)
print(df)

print(input("Stop:"))


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
results = []
cols = []
for attr in dir(talib):
    if attr[:3] == 'CDL':
        print(getattr(talib, attr))
        res = getattr(talib, attr)(df['Open'], df['High'], df['Low'], df['Close'])
        results.append(res)
        cols.append(attr)
        # print(input("Stop:"))
        # print(results)
        # print(cols)
print(results)
print(cols)

if __name__ == '__main__':
    all_candle_list()
