import sqlite3
import pandas as pd
from datetime import datetime


class GetDbDataframe:
    def __init__(self, connection):
        """
        Initialize the GetDbDataframe object.

        Parameters:
        - connection: SQLite database connection object.
        """
        self.connection = connection

    def get_minute_data(self, symbol, interval, lookback):
        """
        Retrieve minute data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the minute data.
        """
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT asset_{interval}m.*, symbols.symbolName as symbol
                        FROM asset_{interval}m
                        JOIN symbols ON asset_{interval}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY asset_{interval}m.id DESC
                        LIMIT {lookback}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id'], axis=1)
        data = data.set_index('Time')
        data.index = pd.to_datetime(data.index)
        change = data.pop("Change")
        data.insert(9, 'Change', change)
        data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
        return data

    def get_crypto_candle(self, symbol, interval, lookback):
        """
        Retrieve crypto candle data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the crypto candle data.
        """
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT cryptoCandle_{interval}m.*
                        FROM cryptoCandle_{interval}m
                        JOIN symbols ON cryptoCandle_{interval}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY cryptoCandle_{interval}m.id DESC
                        LIMIT {lookback}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id', 'asset_id'], axis=1)
        return data

    def get_moving_average(self, symbol, interval, lookback):
        """
        Retrieve moving average data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the moving average data.
        """
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT movingAverage_{interval}m.*
                        FROM movingAverage_{interval}m
                        JOIN symbols ON movingAverage_{interval}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY movingAverage_{interval}m.id DESC
                        LIMIT {lookback}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id', 'asset_id'], axis=1)
        return data

    def get_macd(self, symbol, interval, lookback):
        """
        Retrieve MACD data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the MACD data.
        """
        query = """
            SELECT subquery.*
            FROM (
                SELECT macd_{interval}m.id, macd_{interval}m.signal as macd
                FROM macd_{interval}m
                JOIN symbols ON macd_{interval}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY macd_{interval}m.id DESC
                LIMIT {lookback}
            ) AS subquery
            ORDER BY subquery.id ASC
        """.format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_bollinger_bands(self, symbol, interval, lookback):
        """
        Retrieve Bollinger Bands data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the Bollinger Bands data.
        """
        query = """
            SELECT subquery.*
            FROM (
                SELECT bollingerBands_{interval}m.id, bollingerBands_{interval}m.signal as bollinger_band
                FROM bollingerBands_{interval}m
                JOIN symbols ON bollingerBands_{interval}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY bollingerBands_{interval}m.id DESC
                LIMIT {lookback}
            ) AS subquery
            ORDER BY subquery.id ASC
        """.format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_super_trend(self, symbol, interval, lookback):
        """
        Retrieve Super Trend data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the Super Trend data.
        """
        query = """
            SELECT subquery.*
            FROM (
                SELECT superTrend_{interval}m.id, superTrend_{interval}m.signal as super_trend
                FROM superTrend_{interval}m
                JOIN symbols ON superTrend_{interval}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY superTrend_{interval}m.id DESC
                LIMIT {lookback}
            ) AS subquery
            ORDER BY subquery.id ASC""".format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_rsi(self, symbol, interval, lookback):
        """
        Retrieve RSI data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing the RSI data.
        """
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT rsi_{interval}m.id, rsi_{interval}m.signal as rsi
                        FROM rsi_{interval}m
                        JOIN symbols ON rsi_{interval}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY rsi_{interval}m.id DESC
                        LIMIT {lookback}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(interval=interval, lookback=lookback//interval)

        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_all_indicators(self, symbol, interval, lookback):
        """
        Retrieve all indicators data for a symbol from the database.

        Parameters:
        - symbol: Symbol name.
        - interval: Time interval in minutes.
        - lookback: Number of intervals to retrieve.

        Returns:
        - Pandas DataFrame containing all indicators data.
        """
        df1 = self.get_crypto_candle(symbol, interval, lookback)
        df2 = self.get_moving_average(symbol, interval, lookback)
        df3 = self.get_macd(symbol, interval, lookback)
        df4 = self.get_bollinger_bands(symbol, interval, lookback)
        df5 = self.get_super_trend(symbol, interval, lookback)
        df6 = self.get_rsi(symbol, interval, lookback)

        data = pd.concat([df1, df2, df3, df4, df5, df6], axis=1)
        return data


if __name__ == "__main__":
    connection = sqlite3.connect("big_crypto.db")
    db_frame = GetDbDataframe(connection)
    data = db_frame.get_minute_data("BTCBUSD", 3, 1440)
    print(data)
    indicator = db_frame.get_all_indicators("BTCBUSD", 3, 1440)
    print(indicator)
    print(indicator.sum(axis=1))
