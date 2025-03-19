import talib
import pandas as pd

from api_callling.api_calling import APICall


class MakePattern:
    def __init__(self):
        pass

    def pattern(self, data):
        results = []
        cols = []
        for attr in dir(talib):
            if attr[:3] == 'CDL':
                res = getattr(talib, attr)(data['Open'], data['High'], data['Low'],
                                           data['Close'])
                results.append(res)
                cols.append(attr)
        patterns = pd.concat(results, axis=1)
        patterns.columns = cols
        patterns.astype(int)
        return patterns

if __name__ == "__main__":
    api = APICall()
    from dataframe.dataframe import GetDataframe
    data = GetDataframe(api).get_minute_data('BTCUSDT', 1, 1000)
    make_pattern = MakePattern()
    pattern = make_pattern.pattern(data)
    print(pattern)

