from api_callling.api_calling import APICall
import pandas as pd

# Setting pandas display options
pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Create an instance of APICall to initialize the Binance client
api_instance = APICall()


class GetDataframe:
    def __init__(self, api_instance):
        """
        Initialize GetDataframe with an APICall instance.
        """
        self.api_instance = api_instance  # Store the APICall instance to use its client

    def frame_to_symbol(self, symbol, frame):
        """
        Format raw data into a proper DataFrame with named columns and calculated 'Change' percentage.

        :param symbol: Trading pair symbol (e.g., BTCBUSD)
        :param frame: DataFrame with raw data
        :return: Processed DataFrame
        """
        frame = frame.iloc[:, :10]
        if frame.columns.size > 0:
            frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', f'Volume{symbol[:-4]}', 'CloseTime',
                             f'Volume{symbol[-4:]}', 'Trades', 'BuyQuoteVolume']
            frame = frame.set_index('Time')
            frame.index = pd.to_datetime(frame.index, unit='ms')
            frame = frame.astype(float)
            change = ((frame['Close'] - frame['Open']) * 100) / frame['Open']
            frame['Change'] = change
            frame['symbol'] = symbol
        return frame

    def get_historical_data(self, symbol, interval, lookback, time_unit):
        """
        Fetch and process historical kline (candlestick) data for a specific interval and lookback.

        :param symbol: Trading pair symbol (e.g., BTCBUSD).
        :param interval: Time interval (e.g., 1 for 1 minute).
        :param lookback: How far back to look (e.g., number of candles).
        :param time_unit: Unit of time for lookback ("m" for minutes, "h" for hours, etc.).
        :return: Processed DataFrame of historical data.
        """
        try:
            frame = pd.DataFrame(self.api_instance.client.get_historical_klines(
                symbol, f"{interval}{time_unit}", f"{lookback * interval} {time_unit} ago UTC"
            ))
            return self.frame_to_symbol(symbol, frame)
        except Exception as e:
            print(f"Error fetching historical data for {symbol} ({interval}{time_unit}): {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error

    def get_minute_data(self, symbol, interval, lookback):
        """
        Fetch and process minute-level historical data.
        """
        return self.get_historical_data(symbol, interval, lookback, "m")

    def get_hour_data(self, symbol, interval, lookback):
        """
        Fetch and process hour-level historical data.
        """
        return self.get_historical_data(symbol, interval, lookback, "h")

    def get_day_data(self, symbol, interval, lookback):
        """
        Fetch and process daily-level historical data.
        """
        return self.get_historical_data(symbol, interval, lookback, "d")

    def get_week_data(self, symbol, interval, lookback):
        """
        Fetch and process week-level historical data.
        """
        return self.get_historical_data(symbol, interval, lookback, "w")

    def get_month_data(self, symbol, interval, lookback):
        """
        Fetch and process month-level historical data.
        """
        return self.get_historical_data(symbol, interval, lookback, "M")

    def get_range_data(self, symbol, interval, start_time, end_time):
        """
        Fetch historical data for a specific time range.
        """
        try:
            frame = pd.DataFrame(self.api_instance.client.get_historical_klines(
                symbol, f"{interval}m", start_time, end_time
            ))
            return self.frame_to_symbol(symbol, frame)
        except Exception as e:
            print(f"Error fetching range data for {symbol} ({start_time} to {end_time}): {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error

    def get_complex_dataFrame(self, symbol, interval, lookback, timeduration=15):
        """
        Fetch and resample minute data into a higher time interval.
        """
        df = self.get_minute_data(symbol, interval, lookback)
        if not df.empty:
            df = df.resample(f"{timeduration}T").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})
        return df

    def data_function(self, symbol, interval, lookback):
        """
        Wrapper to fetch minute-level data.
        """
        return self.get_minute_data(symbol, interval, lookback)


if __name__ == "__main__":
    # Create an instance of GetDataframe with the `api_instance`
    data_f = GetDataframe(api_instance)

    # Test 1: Fetch and display 1 day of minute-level candle data for BTCBUSD
    print("Fetching 1 day of minute-level data (BTCUSDT)...")
    df_minute = data_f.get_minute_data('BTCUSDT', 1, 1440)  # 1440 minutes = 1 day
    print(df_minute)

    # Test 2: Fetch and display 1 day of hour-level candle data for BTCBUSD
    print("Fetching 30 days of daily-level data (BTCUSDT)...")
    df_day = data_f.get_day_data('BTCUSDT', 1, 30)
    print(df_day)

    # Test 3: Fetch and resample as complex 15-minute timeframe
    print("Fetching and resampling minute-level data to 15-minute intervals (BTCUSDT)...")
    df_complex = data_f.get_complex_dataFrame('BTCUSDT', 1, 1440, timeduration=15)
    print(df_complex)
