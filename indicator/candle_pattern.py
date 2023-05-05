import talib
import pandas as pd

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
        patterns = pd.DataFrame(results).T
        patterns.columns = cols
        patterns.astype(int)
        return patterns

if __name__ == "__main__":
    from database.dataframe import GetDataframe
    data = GetDataframe().get_minute_data('BTCBUSD', 1, 1000)
    make_pattern = MakePattern()
    pattern = make_pattern.pattern(data)
    print(pattern)