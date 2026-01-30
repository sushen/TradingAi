"""
Script Name: resample.py
Author: Sushen Biswas
Date: 2023-03-26
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd


from api_callling.api_calling import APICall


class ResampleData:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol
        self.aggregation = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "VolumeBTC": "sum",
            "Change": "sum",
            "CloseTime": "last",
            "VolumeUSDT": "sum",
            "Trades": "sum",
            "BuyQuoteVolume": "sum",
            "symbol": "first",
            "Time": lambda x: pd.to_datetime(x.iloc[-1], unit="ms")

        }

    def resample_to_minute(self, df, minute):
        time = minute

        # Dynamically filter aggregation dictionary based on existing columns in df
        agg_filtered = {key: func for key, func in self.aggregation.items() if key in df}

        if not agg_filtered:
            raise ValueError("No matching columns in DataFrame for resampling.")

        # Perform resampling using the filtered aggregation
        return df.resample(f"{time}T").agg(agg_filtered)[-len(df) // minute:]

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
    from dataframe.dataframe import GetDataframe
    from dataframe.future_dataframe import GetFutureDataframe

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
