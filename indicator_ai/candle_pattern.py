import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

import talib
import pandas as pd
from api_callling.api_calling import APICall


class MakeCandlePattern:
    def __init__(self):
        pass

    def pattern(self, data):
        results = []
        cols = []

        # Ensure 'CloseTime' exists in the data
        # if 'CloseTime' not in data.columns:
        #     raise KeyError("'CloseTime' column is missing in the data.")
        #
        time_column = data['CloseTime']

        # Apply the TA-Lib functions for candlestick patterns
        for attr in dir(talib):
            if attr[:3] == 'CDL':  # Look for candlestick pattern functions in TA-Lib
                res = getattr(talib, attr)(data['Open'], data['High'], data['Low'], data['Close'])
                results.append(res)
                cols.append(attr)

        # Create the pattern DataFrame
        patterns = pd.concat(results, axis=1)
        patterns.columns = cols

        # Directly use 'CloseTime' as 'Time' column without converting to datetime
        patterns['CloseTime'] = time_column  # No need to convert to datetime since it already is

        # Ensure the columns are of the right types
        patterns = patterns.astype({'CloseTime': 'int64'})  # Use integer Unix timestamp for 'Time'

        return patterns


if __name__ == "__main__":
    api = APICall()
    from database_ai.dataframe import GetDataframe

    # Fetch the data (Ensure the data contains CloseTime column)
    data = GetDataframe(api).get_minute_data('BTCUSDT', 1, 1000)
    print(data)

    make_pattern = MakeCandlePattern()
    pattern = make_pattern.pattern(data)

    print(pattern)
