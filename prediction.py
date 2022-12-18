import time
import pandas as pd
import talib
import joblib
from datetime import datetime
from sty import fg
from playsound import playsound
import warnings
warnings.filterwarnings('ignore')
from dataframe import GetDataframe

def feature(symbol):
    df = GetDataframe().get_minute_data(symbol, 1, 6)
    df = df.iloc[:,0:10]

    df.astype(float)
    # df = df.drop(columns=['symbol','VolumeBUSD', 'CloseTime'])
    # df = df.iloc[0]
    # print(df)

    print(f"Current Bitcoin Price: {df.iloc[-2]['Close']}")
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

    for cp in patterns:
        single_cp = patterns[f'{cp}']
        for i in single_cp:
            if i >= 100 or i <= -100:
                print(f"Candle Name : {cp}, Status :{i}")

    patterns["Sum"] = patterns.sum(axis=1)

    print(patterns['Sum'])

    for i in patterns["Sum"]:
        if i >= 200 or i <= -200:
            playsound('sounds/Bearish.wav')
            # print(input("....:"))

    print(patterns)

    df = df.add(patterns, fill_value=0)
    df = df.drop(['CloseTime', 'Sum'], axis=1)
    df = df.iloc[-2]
    # print(df)
    return df


while True:
    df = feature("BTCBUSD")
    model = joblib.load("btcbusd_trand_predictor.joblib")
    predictions = model.predict([df])
    # print(predictions)

    if predictions[0] >= 100:
        print("The Bullish sound")
        playsound('sounds/Bearish.wav')
    elif predictions[0] <= -100:
        print("The Bearish sound")
        playsound('Bullish.wav')
    else:
        print(f"Market have no movement and Model Prediction is {predictions[0]}.")

    pred = fg.green + str(datetime.now()) + ' : ' + fg.rs + str(predictions)
    print(pred)
    print(".......................\n")

    time.sleep(60)


