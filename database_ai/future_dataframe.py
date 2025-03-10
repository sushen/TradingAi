import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script_name = os.path.basename(__file__)
print(f"fine name: {script_name} ")

from datetime import timedelta
import datetime
import pytz
import pandas as pd

from database.dataframe import GetDataframe  # Corrected Import Path
from api_callling.api_calling import APICall



class GetFutureDataframe(GetDataframe):
    def __init__(self):
        # Instantiate APICall and pass it to the parent class initializer
        api_instance = APICall()
        super().__init__(api_instance)  # Pass the api_instance to the parent class initializer

    def get_month_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(
            self.api_instance.client.futures_klines(symbol=symbol, interval=f"{interval}M", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_week_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(
            self.api_instance.client.futures_klines(symbol=symbol, interval=f"{interval}w", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_day_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(
            self.api_instance.client.futures_klines(symbol=symbol, interval=f"{interval}d", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_hour_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(
            self.api_instance.client.futures_klines(symbol=symbol, interval=f"{interval}h", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_minute_data(self, symbol, interval, lookback):
        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(minutes=lookback * interval)
        end_time = current_time
        return self.get_range_data(symbol, interval, start_time, end_time)

    def get_range_data(self, symbol, interval, start_time, end_time):
        data = []
        num_calls = (end_time - start_time) // timedelta(minutes=500 * interval) + 1

        for i in range(num_calls):
            start_timestamp = int(start_time.timestamp() * 1000)
            end_timestamp = int((start_time + timedelta(minutes=500 * interval)).timestamp() * 1000)
            klines = self.api_instance.client.futures_klines(
                symbol=symbol,
                interval=f"{interval}m",
                startTime=start_timestamp,
                endTime=end_timestamp
            )
            if klines:
                data.extend(klines)

            start_time += timedelta(minutes=500 * interval)

        if data:
            frame = pd.DataFrame(data)
            frame = self.frame_to_symbol(symbol, frame)
            return frame
        else:
            return pd.DataFrame()


if __name__ == "__main__":
    # Initialize the GetFutureDataframe object
    data_f = GetFutureDataframe()

    # Example 1: Fetch 1 day of minute-level data for BTCUSDT
    print("Fetching 1 day of minute-level data...")
    data = data_f.get_minute_data('BTCUSDT', 1, 1440)  # 1440 minutes = 1 day
    print(data)
    print(f"Number of rows: {len(data)}")

    # Example 2: Fetch range data from a specific start and end time
    current_time = datetime.datetime.now(pytz.utc)
    start_time = datetime.datetime.strptime("2023-05-14 17:45:00", "%Y-%m-%d %H:%M:%S")
    start_time = start_time.replace(tzinfo=pytz.utc)  # Make start_time offset-aware
    start_time += timedelta(minutes=1)
    end_time = current_time

    print("\nFetching range data for BTCUSDT...")
    print(f"Start Time: {start_time}")
    print(f"End Time: {end_time}")

    # range_data = data_f.get_range_data('BTCUSDT', 1, start_time, end_time)
    # print(range_data)
    # print(f"Number of rows: {len(range_data)}")
