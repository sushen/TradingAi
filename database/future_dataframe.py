from dataframe import GetDataframe
import pandas as pd
from api_callling.api_calling import APICall

class GetFutureDataframe(GetDataframe):

    def get_month_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}M", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_week_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}w", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_day_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}d", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_hour_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}h", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_minute_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.futures_klines(symbol=symbol, interval=f"{interval}m", limit=lookback))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

if __name__ == "__main__":
    data_f = GetFutureDataframe()
    print(data_f.get_minute_data('BTCBUSD', 1, 10))
    print(data_f.get_minute_data('BTCBUSD', 3, 10))