import pandas as pd
import talib
from dataframe import GetDataframe

df = GetDataframe().get_minute_data("BTCBUSD", 1, 10)
df = df.iloc[:, 0:10]
df.astype(float)
# df = df.drop(columns=['symbol','VolumeBUSD', 'CloseTime'])
# df = df.iloc[0]
# print(df)
print(f"Current Bitcoin Price: {df.iloc[-2]['Close']}")
results = []
cols = []
for attr in dir(talib):
    if attr[:3] == 'CDL':
        #         print(getattr(talib, attr))
        res = getattr(talib, attr)(df['Open'], df['High'], df['Low'],
                                   df['Close'])
        results.append(res)
        cols.append(attr)
# print(results)
# print(cols)

patterns = pd.DataFrame(results).T
patterns.columns = cols
patterns.astype(float)
patterns["Sum"] = patterns.sum(axis=1)
# print(patterns)

for cp in patterns:
    single_cp = patterns[f'{cp}']
    for i in single_cp:
        if i > 0 or i < 0:
            print(f"Candle Name : {cp} Status :{i}")


# print(patterns['Sum'])
df = df.add(patterns, fill_value=0)
df = df.drop(['CloseTime', 'Sum'], axis=1)
df = df.iloc[-2]
# print(df)
