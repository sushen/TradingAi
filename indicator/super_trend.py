import matplotlib.pyplot as plt
from database.dataframe import GetDataframe
import pandas as pd
import numpy as np
import talib

class SuperTrend:
    def __init__(self):
        pass

    def create_super_trend(self, df):
        data = pd.DataFrame({'price': df['Close']})
        data['st'], data['upt'], data['dt'] = self.get_super_trend(df['High'], df['Low'], df['Close'], 10, 3)

        data['signal'] = 0
        data.loc[(data['dt'].notna()) & (data['dt'].shift(1).isna()), 'signal'] = -100
        data.loc[(data['dt'].shift(1).notna()) & (data['dt'].isna()), 'signal'] = 100
        data['signal'].fillna(0, inplace=True)
        return data

    def get_super_trend(self, high, low, close, lookback, multiplier):
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
        atr = tr.ewm(lookback).mean()

        # H/L AVG AND BASIC UPPER & LOWER BAND
        hl_avg = (high + low) / 2
        upper_band = (hl_avg + multiplier * atr).dropna()
        lower_band = (hl_avg - multiplier * atr).dropna()

        # FINAL UPPER BAND
        final_bands = pd.DataFrame(columns = ['upper', 'lower'])
        final_bands.iloc[:,0] = [x for x in upper_band - upper_band]
        final_bands.iloc[:,1] = final_bands.iloc[:,0]
        for i in range(len(final_bands)):
            if i == 0:
                final_bands.iloc[i,0] = 0
            else:
                if (upper_band[i] < final_bands.iloc[i-1,0]) | (close[i-1] > final_bands.iloc[i-1,0]):
                    final_bands.iloc[i,0] = upper_band[i]
                else:
                    final_bands.iloc[i,0] = final_bands.iloc[i-1,0]

        # FINAL LOWER BAND
        for i in range(len(final_bands)):
            if i == 0:
                final_bands.iloc[i, 1] = 0
            else:
                if (lower_band[i] > final_bands.iloc[i-1,1]) | (close[i-1] < final_bands.iloc[i-1,1]):
                    final_bands.iloc[i,1] = lower_band[i]
                else:
                    final_bands.iloc[i,1] = final_bands.iloc[i-1,1]

        # SUPERTREND
        supertrend = pd.DataFrame(columns = [f'supertrend_{lookback}'])
        supertrend.iloc[:,0] = [x for x in final_bands['upper'] - final_bands['upper']]

        for i in range(len(supertrend)):
            if i == 0:
                supertrend.iloc[i, 0] = 0
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] < final_bands.iloc[i, 0]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] > final_bands.iloc[i, 0]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] > final_bands.iloc[i, 1]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] < final_bands.iloc[i, 1]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 0]

        supertrend = supertrend.set_index(upper_band.index)
        supertrend = supertrend.dropna()[1:]

        # ST UPTREND/DOWNTREND
        upt = []
        dt = []
        close = close.iloc[len(close) - len(supertrend):]

        for i in range(len(supertrend)):
            if close[i] > supertrend.iloc[i, 0]:
                upt.append(supertrend.iloc[i, 0])
                dt.append(np.nan)
            elif close[i] < supertrend.iloc[i, 0]:
                upt.append(np.nan)
                dt.append(supertrend.iloc[i, 0])
            else:
                upt.append(np.nan)
                dt.append(np.nan)

        st, upt, dt = pd.Series(supertrend.iloc[:, 0]), pd.Series(upt), pd.Series(dt)
        upt.index, dt.index = supertrend.index, supertrend.index

        return st, upt, dt

    def plot_super_trend(self, df, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(df['price'], linewidth=2, label='CLOSING PRICE')
        ax.plot(df['st'], color='green', linewidth=2, label='ST UPTREND 10,3')
        ax.plot(df['dt'], color='r', linewidth=2, label='ST DOWNTREND 10,3')

        ax.scatter(df.index[df['signal'] == 100], df['price'][df['signal'] == 100],
                    marker='^', s=50, color='green', label='Buy signal', zorder=3)
        ax.scatter(df.index[df['signal'] == -100], df['price'][df['signal'] == -100],
                    marker='v', s=50, color='red', label='Sell signal', zorder=3)

        # plt.scatter(df.index[df['signal2'] == 100], df['Close'][df['signal2'] == 100],
        #             marker='^', s=20, color='grey', label='Buy signal', zorder=3)
        # plt.scatter(df.index[df['signal2'] == -100], df['Close'][df['signal2'] == -100],
        #             marker='v', s=20, color='black', label='Sell signal', zorder=3)

        ax.set_title('Super Trend')
        ax.legend(loc='upper left')
        # plt.show()
        return ax

    def create_super_trend_talib(self, df):
        # Calculate SuperTrend
        sptrend = talib.STOCHF(df['High'], df['Low'], df['Close'], fastk_period=10, fastd_period=3)
        sptrend = pd.Series(sptrend[0])
        df['sptrend'] = sptrend.values
        df['signal2'] = 0
        df.loc[(df['sptrend'].notna()) & (df['sptrend'] <= 0), 'signal2'] = -100
        df.loc[(df['sptrend'].notna()) & (df['sptrend'] >= 100), 'signal2'] = 100
        df['signal2'].fillna(0, inplace=True)

if __name__ == "__main__":
    # Load data
    df = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    df = df.iloc[:, 1:7]
    df.rename(columns={'VolumeBTC': 'volume'}, inplace=True)
    df.index = df.index.rename('datetime')
    df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)
    print(df)
    st = SuperTrend()
    df = st.create_super_trend(df)
    # df = st.create_super_trend_talib(df)
    # print(df[['st', 'dt', 'signal', 'sptrend', 'signal2']][600:])
    print(df[['st', 'dt', 'signal']][600:])
    ax = st.plot_super_trend(df)
    plt.show()

