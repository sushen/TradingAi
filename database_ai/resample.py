"""
Script Name: resample.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

from api_callling.api_calling import APICall


class ResampleData:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol
        self.aggregation = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            'VolumeBTC': "sum",
            "Change": "last",
            "CloseTime": "last",
            "VolumeUSDT": "sum",
            "Trades": "sum",
            "BuyQuoteVolume": "sum",
            "symbol": "first",
            "Time": "first"
        }

    def resample_to_minute(self, df, minute):
        # Ensure 'CloseTime' is part of the DataFrame and convert it to datetime
        df['CloseTime'] = pd.to_datetime(df['CloseTime'], unit='ms')  # Assuming CloseTime is in milliseconds

        # Set 'CloseTime' as the index
        df.set_index('CloseTime', inplace=True)

        # Create aggregation dictionary dynamically, ensuring only valid columns are included
        agg_filtered = {key: func for key, func in self.aggregation.items() if key in df.columns}

        if not agg_filtered:
            raise ValueError("No matching columns in DataFrame for resampling.")

        # Perform resampling
        resampled_df = df.resample(f"{minute}T").agg(agg_filtered)

        # Reset index to keep 'Time' as a normal column and avoid duplicate index
        resampled_df.reset_index(drop=False, inplace=True)

        print(resampled_df)

        return resampled_df

    def resample_to_hours(self, df, hour):
        time = hour * 60
        agg_filtered = {key: func for key, func in self.aggregation.items() if key in df}
        return df.resample(f"{time}T").agg(agg_filtered)

    def resample_to_day(self, df, day):
        time = day * 24 * 60
        agg_filtered = {key: func for key, func in self.aggregation.items() if key in df}
        return df.resample(f"{time}T").agg(agg_filtered)


if __name__ == "__main__":
    api = APICall()
    from dataframe import GetDataframe
    from database.future_dataframe import GetFutureDataframe

    symbol = "BTCUSDT"

    # Example usage
    data = GetDataframe(api).get_minute_data(symbol, 1, 60)
    data = data.rename_axis('Time_index')
    data['Time'] = data.index
    print(data)

    rd = ResampleData(symbol)
    new_data = rd.resample_to_minute(data, 30)
    print(new_data)

    # data = GetDataframe().get_minute_data(symbol, 30, 2)
    # data = data.rename_axis('Time_index')
    # data['Time'] = data.index
    # print(data)
