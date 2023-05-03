import talib
import pandas as pd

class MakePattern:
    def __init__(self, open, high, low, close):
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def rsi(self):
        # Create an empty DataFrame with two columns
        df = pd.DataFrame(columns=['rsi', 'rsisignal'])
        df['rsi'] = talib.RSI(self.close, timeperiod=5)

        df['rsisignal'] = 0
        df.loc[df['rsi'] > 70, 'rsisignal'] = -100
        df.loc[df['rsi'] < 30, 'rsisignal'] = 100

        return df

    def pattern(self):
        results = []
        cols = []
        for attr in dir(talib):
            if attr[:3] == 'CDL':
                res = getattr(talib, attr)(self.open, self.high, self.low,
                                           self.close)
                results.append(res)
                cols.append(attr)
        patterns = pd.DataFrame(results).T
        patterns.columns = cols
        patterns.astype(int)
        return patterns
