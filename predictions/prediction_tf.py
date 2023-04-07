import time
import pandas as pd
import talib
import joblib
from datetime import datetime
from sty import fg
from playsound import playsound
import warnings
import numpy as np
from database.exchange_info import BinanceExchange
import contextlib
import io
import pickle

from googlesheet.connection import Connection

warnings.filterwarnings('ignore')
from database.dataframe import GetDataframe

ws = Connection().connect_worksheet("tracker")

def feature(symbol):
    df = GetDataframe().get_minute_data(symbol, 1, 8)

    if df is None:
        return

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
    #TODO: We need to fixed it
    # df['rsi'] = talib.RSI(df['Close'], timeperiod=14)
    # print(data['rsi'].to_string())

    # Generate signals
    # df['signal'] = 0
    # df.loc[df['rsi'] > 70, 'signal'] = -100
    # df.loc[df['rsi'] < 30, 'signal'] = 100


    patterns = pd.DataFrame(results).T
    patterns.columns = cols
    patterns.astype(float)

    # patterns['rsi'] = df['rsi']

    for cp in patterns:
        single_cp = patterns[f'{cp}']
        for i in single_cp:
            if i >= 100 or i <= -100:
                print(f"Candle Name : {cp}, Status :{i}")

    patterns["Sum"] = patterns.sum(axis=1)

    print(patterns['Sum'])

    for i in patterns["Sum"]:
        if i >= 400 or i <= -400:
            playsound('sounds/Bearish.wav')
            # print(input("....:"))

    print(patterns)

    df = df.add(patterns, fill_value=0)
    df = df.drop(['CloseTime', 'Sum'], axis=1)
    df = df.iloc[-2]
    # print(df)

    body = [str(datetime.now()), int(patterns["Sum"][-2])]  # the values should be a list
    ws.append_row(body, table_range="D1")

    return df


# with contextlib.redirect_stdout(io.StringIO()):
#     model = joblib.load("../trained_model/btcbusd_trand_predictor_tf.joblib")
# TODO: Use Decision tree also Model
with open("../trained_model/btcbusd_trand_predictor_tf.joblib", "rb") as f:
    model = pickle.load(f)

# Define the target values
targets = np.arange(-3000, 3001, 100)

be = BinanceExchange()
all_symbols = be.get_specific_symbols(contractType="PERPETUAL", quoteAsset='BUSD')

# TODO: Handle api exception by dealing time
while True:
    for symbol in all_symbols:

        print()
        print("PREDICTING FOR: ", symbol.upper())
        print()

        df = feature(symbol)

        if df is None:
            continue

        predictions = model.predict(pd.DataFrame(df).transpose())
        predictions = np.array([targets[np.abs(targets - val).argmin()] for val in predictions])
        print(predictions[0])
        body = [str(datetime.now()), int(predictions[0])]  # the values should be a list
        ws.append_row(body, table_range="A1")

        if predictions[0] >= 100:
            print("The Bullish sound")
            # playsound('sounds/Bearish.wav')

        elif predictions[0] <= -100:
            print("The Bearish sound")
            # playsound('sounds/Bullish.wav')

        else:
            print(f"Market have no movement and Model Prediction is {predictions[0]}.")

        pred = fg.green + str(datetime.now()) + ' : ' + fg.rs + str(predictions[0])
        # print(pred)
        print(".......................\n")
        time.sleep(10)
    time.sleep(60)
