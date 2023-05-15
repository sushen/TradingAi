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
        frames = []
        num_calls = lookback // 1500 + 1
        for i in range(num_calls):
            start_timestamp = int((pd.Timestamp.now() - pd.DateOffset(minutes=(i + 1) * 1500 * interval)).timestamp() * 1000)
            end_timestamp = int((pd.Timestamp.now() - pd.DateOffset(minutes=i * 1500 * interval)).timestamp() * 1000)
            klines = APICall.client.futures_klines(symbol=symbol, interval=f"{interval}m", limit=1500,
                                                startTime=start_timestamp, endTime=end_timestamp)

            if klines:
                frame = pd.DataFrame(klines)
                frames.append(frame)
            print(i)

        if frames:
            result_frame = pd.concat(frames, ignore_index=True)
            result_frame = self.frame_to_symbol(symbol, result_frame)
            return result_frame
        else:
            return pd.DataFrame()


if __name__ == "__main__":
    data_f = GetFutureDataframe()
    print(data_f.get_minute_data('BTCBUSD', 1, 4*30*1400))
    print(data_f.get_minute_data('BTCBUSD', 3, 10))