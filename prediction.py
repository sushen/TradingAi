import time

import pandas as pd
import talib
import joblib

from dataframe import GetDataframe
symbol = "BTCBUSD"

while True:
    df = GetDataframe().get_minute_data(symbol, 1, 5)
    df = df.iloc[:,0:10]
    df.astype(float)
    # df = df.drop(columns=['symbol','VolumeBUSD', 'CloseTime'])
    # df = df.iloc[0]
    print(df)
    results = []
    cols = []
    for attr in dir(talib):
        if attr[:3]=='CDL':
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
    # patterns
    print(patterns)
    df = df.add(patterns, fill_value=0)
    df = df.drop(['VolumeBUSD', 'CloseTime', 'Sum'], axis=1)
    df = df.iloc[-2]
    print(df)
    # print(model.predict([df]))


    model = joblib.load("btcbusd_trand_predictor.joblib")
    predictions = model.predict([df])
    print(predictions)
    time.sleep(60)
