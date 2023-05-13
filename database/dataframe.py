from api_callling.api_calling import APICall

import pandas as pd

pd.set_option('mode.chained_assignment', None)

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class GetDataframe:

    def frame_to_symbol(self, symbol, frame):
        # print(frame)
        frame = frame.iloc[:, :10]
        # print(frame)
        # print("\n")
        if frame.columns.size > 0:
            frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', f'Volume{symbol[:-4]}', 'CloseTime',
                             f'Volume{symbol[-4:]}', 'Trades', 'BuyQuoteVolume']
            frame = frame.set_index('Time')
            frame.index = pd.to_datetime(frame.index, unit='ms')
            frame = frame.astype(float)
            change = ((frame['Close'] - frame['Open']) * 100) / frame['Open']
            frame['Change'] = change
            frame['symbol'] = symbol
            # print(frame)
            return frame

    # TODO : This candle historical data come from SOPT market it should come from future market
    def get_month_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.get_historical_klines(symbol, f"{interval}M", f"{lookback * interval} month ago UTC"))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_week_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.get_historical_klines(symbol, f"{interval}w", f"{lookback * interval} week ago UTC"))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_day_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.get_historical_klines(symbol, f"{interval}d", f"{lookback * interval} day ago UTC"))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_hour_data(self, symbol, interval, lookback):
        frame = pd.DataFrame(APICall.client.get_historical_klines(symbol, f"{interval}h", f"{lookback * interval} hour ago UTC"))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_minute_data(self, symbol, interval, lookback):
        # TODO: interval and look back text have to recheck
        frame = pd.DataFrame(APICall.client.get_historical_klines(symbol, f"{interval}m", f"{lookback * interval} min ago UTC"))
        frame = self.frame_to_symbol(symbol, frame)
        return frame

    def get_range_data(self, symbol, interval, start_time, end_time):
        frame = pd.DataFrame(
            APICall.client.get_historical_klines(symbol, f"{interval}m", f"{start_time}", f"{end_time}"))
        frame = self.frame_to_symbol(symbol, frame)
        # try:
        #     frame = pd.DataFrame(APICall.client.get_historical_klines(symbol, f"{interval}m", f"{lookback} min ago UTC"))
        #     frame = self.frame_to_symbol(symbol, frame)
        # except:
        #     print(symbol)
        #     print(input("stop :"))
        #     pass

        # print(frame)
        return frame

    # Creat New Timeline Candle
    def get_complex_dataFrame(self, symbol, interval, lookback, timeduration=15):
        df = self.get_minute_data(symbol, interval, lookback)
        df = df.resample(f"{timeduration}T").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})
        return df

    def data_function(self, symbol, interval, lookback):
        return self.get_minute_data(symbol, interval, lookback)


if __name__ == "__main__":
    data_f = GetDataframe()
    # print(data_f.get_complex_dataFrame('BTCBUSD', 1, 1000, 3))
    # print(data_f.data_function('BTCBUSD', 1, 1))

    print(GetDataframe().get_minute_data('BTCBUSD', 1, 10))
    # frame = pd.DataFrame(APICall.client.get_historical_klines('SOLBUSD', "3m", "3 min ago UTC"))
    # print(frame)
    print(pd.DataFrame(APICall.client.futures_klines(symbol="BTCBUSD", interval=APICall.client.KLINE_INTERVAL_1MINUTE, limit=10)))