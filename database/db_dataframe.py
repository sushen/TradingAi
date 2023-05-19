import sqlite3
import pandas as pd
from datetime import datetime

class GetDbDataframe:
    def __init__(self, connection):
        # Connect to the database
        self.connection = connection

    def get_minute_data(self, symbol, time, limit):
        # Execute the SQL query to fetch the last 250 records in ascending order
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT asset_{time}m.*, symbols.symbolName as symbol
                        FROM asset_{time}m
                        JOIN symbols ON asset_{time}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY asset_{time}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(time=time, limit=limit//time)

        data = pd.read_sql_query(query, self.connection, params=(symbol, ))
        data = data.drop(['id', 'symbol_id'], axis=1)
        data = data.set_index('Time')
        change = data.pop("Change")
        data.insert(9, 'Change', change)
        data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
        return data

    def get_crypto_candle(self, symbol, time, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT cryptoCandle_{time}m.*
                        FROM cryptoCandle_{time}m
                        JOIN symbols ON cryptoCandle_{time}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY cryptoCandle_{time}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(time=time, limit=limit // time)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id', 'asset_id'], axis=1)
        return data

    def get_moving_average(self, symbol, time, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT movingAverage_{time}m.*
                        FROM movingAverage_{time}m
                        JOIN symbols ON movingAverage_{time}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY movingAverage_{time}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(time=time, limit=limit // time)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id', 'asset_id'], axis=1)
        return data

    def get_macd(self, symbol, time, limit):
        query = """
            SELECT subquery.*
            FROM (
                SELECT macd_{time}m.id, macd_{time}m.signal as macd
                FROM macd_{time}m
                JOIN symbols ON macd_{time}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY macd_{time}m.id DESC
                LIMIT {limit}
            ) AS subquery
            ORDER BY subquery.id ASC
        """.format(time=time, limit=limit // time)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_bollinger_bands(self, symbol, time, limit):
        query = """
            SELECT subquery.*
            FROM (
                SELECT bollingerBands_{time}m.id, bollingerBands_{time}m.signal as bollinger_band
                FROM bollingerBands_{time}m
                JOIN symbols ON bollingerBands_{time}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY bollingerBands_{time}m.id DESC
                LIMIT {limit}
            ) AS subquery
            ORDER BY subquery.id ASC
        """.format(time=time, limit=limit // time)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_super_trend(self, symbol, time, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT superTrend_{time}m.id, superTrend_{time}m.signal as super_trend
                        FROM superTrend_{time}m
                        JOIN symbols ON superTrend_{time}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY superTrend_{time}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(time=time, limit=limit // time)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_rsi(self, symbol, time, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT rsi_{time}m.id, rsi_{time}m.signal as rsi
                        FROM rsi_{time}m
                        JOIN symbols ON rsi_{time}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY rsi_{time}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(time=time, limit=limit // time)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_all_indicators(self, symbol, time, limit):

        df1 = self.get_crypto_candle(symbol, time, limit)
        df2 = self.get_moving_average(symbol, time, limit)
        df3 = self.get_macd(symbol, time, limit)
        df4 = self.get_bollinger_bands(symbol, time, limit)
        df5 = self.get_super_trend(symbol, time, limit)
        df6 = self.get_rsi(symbol, time, limit)

        data = pd.concat([df1, df2, df3, df4, df5, df6], axis=1)

        return data


if __name__ == "__main__":
    connection = sqlite3.connect("big_crypto.db")
    db_frame = GetDbDataframe(connection)
    data = db_frame.get_minute_data("BTCBUSD", 1, 30*1440)
    print(data)
    indicator = db_frame.get_all_indicators("BTCBUSD", 1, 30*1440)
    print(indicator)