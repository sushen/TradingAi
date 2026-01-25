import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import timedelta
import datetime
import pytz
import pandas as pd

from dataframe.base_dataframe import GetDataframe
from api_callling.api_calling import APICall
from api_callling.safe_binance import safe_futures_klines  # ✅ SAFE WRAPPER


class GetFutureDataframe(GetDataframe):
    def __init__(self):
        # SINGLE shared API instance (singleton client inside)
        api_instance = APICall()
        super().__init__(api_instance)

    # --------------------------------------------------
    # LOWER-RISK CALLS (simple lookbacks)
    # --------------------------------------------------

    def get_month_data(self, symbol, interval, lookback):
        klines = safe_futures_klines(
            self.api_instance,
            symbol=symbol,
            interval=f"{interval}M",
            limit=lookback
        )
        if not klines:
            return pd.DataFrame()

        frame = pd.DataFrame(klines)
        return self.frame_to_symbol(symbol, frame)

    def get_week_data(self, symbol, interval, lookback):
        klines = safe_futures_klines(
            self.api_instance,
            symbol=symbol,
            interval=f"{interval}w",
            limit=lookback
        )
        if not klines:
            return pd.DataFrame()

        frame = pd.DataFrame(klines)
        return self.frame_to_symbol(symbol, frame)

    def get_day_data(self, symbol, interval, lookback):
        klines = safe_futures_klines(
            self.api_instance,
            symbol=symbol,
            interval=f"{interval}d",
            limit=lookback
        )
        if not klines:
            return pd.DataFrame()

        frame = pd.DataFrame(klines)
        return self.frame_to_symbol(symbol, frame)

    def get_hour_data(self, symbol, interval, lookback):
        klines = safe_futures_klines(
            self.api_instance,
            symbol=symbol,
            interval=f"{interval}h",
            limit=lookback
        )
        if not klines:
            return pd.DataFrame()

        frame = pd.DataFrame(klines)
        return self.frame_to_symbol(symbol, frame)

    # --------------------------------------------------
    # HIGH-RISK CALL (this caused your crash)
    # --------------------------------------------------

    def get_minute_data(self, symbol, interval, lookback):
        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(minutes=lookback * interval)
        end_time = current_time
        return self.get_range_data(symbol, interval, start_time, end_time)

    def get_range_data(self, symbol, interval, start_time, end_time):
        """
        SAFE range fetch with reconnect + retry.
        This is the critical fix for ConnectionResetError (10054).
        """
        data = []
        num_calls = (end_time - start_time) // timedelta(minutes=500 * interval) + 1

        for _ in range(num_calls):
            start_timestamp = int(start_time.timestamp() * 1000)
            end_timestamp = int(
                (start_time + timedelta(minutes=500 * interval)).timestamp() * 1000
            )

            klines = safe_futures_klines(
                self.api_instance,
                symbol=symbol,
                interval=f"{interval}m",
                startTime=start_timestamp,
                endTime=end_timestamp
            )

            if klines:
                data.extend(klines)

            start_time += timedelta(minutes=500 * interval)

        if not data:
            return pd.DataFrame()

        frame = pd.DataFrame(data)
        return self.frame_to_symbol(symbol, frame)


# --------------------------------------------------
# TEST BLOCK (OPTIONAL)
# --------------------------------------------------
if __name__ == "__main__":
    data_f = GetFutureDataframe()

    print("Fetching 1 day of minute-level data...")
    data = data_f.get_minute_data("BTCUSDT", 1, 1440)
    print(data)
    print(f"Rows: {len(data)}")

    current_time = datetime.datetime.now(pytz.utc)
    start_time = datetime.datetime.strptime(
        "2023-05-14 17:45:00", "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=pytz.utc) + timedelta(minutes=1)

    print("\nFetching range data...")
    range_data = data_f.get_range_data("BTCUSDT", 1, start_time, current_time)
    print(range_data)
    print(f"Rows: {len(range_data)}")
