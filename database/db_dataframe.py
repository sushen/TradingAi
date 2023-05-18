import sqlite3
import pandas as pd
from datetime import datetime

class GetDbDataframe:
    def __init__(self):
        # Connect to the database
        self.connection = sqlite3.connect("big_crypto.db")

    def get_minute_data(self, symbol, t, limit):
        # Execute the SQL query to fetch the last 250 records in ascending order
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT asset_{t}m.*, symbols.symbolName as symbol
                        FROM asset_{t}m
                        JOIN symbols ON asset_{t}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY asset_{t}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(t=t, limit=limit//t)

        data = pd.read_sql_query(query, self.connection, params=(symbol, ))
        data = data.drop(['id', 'symbol_id'], axis=1)
        data = data.set_index('Time')
        change = data.pop("Change")
        data.insert(9, 'Change', change)
        data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
        return data

    def get_crypto_candle(self, symbol, t, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT cryptoCandle_{t}m.*
                        FROM cryptoCandle_{t}m
                        JOIN symbols ON cryptoCandle_{t}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY cryptoCandle_{t}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(t=t, limit=limit // t)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id', 'asset_id'], axis=1)
        return data

    def get_moving_average(self, symbol, t, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT movingAverage_{t}m.*
                        FROM movingAverage_{t}m
                        JOIN symbols ON movingAverage_{t}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY movingAverage_{t}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(t=t, limit=limit // t)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'symbol_id', 'asset_id'], axis=1)
        return data

    def get_macd(self, symbol, t, limit):
        query = """
            SELECT subquery.*
            FROM (
                SELECT macd_{t}m.id, macd_{t}m.signal as macd
                FROM macd_{t}m
                JOIN symbols ON macd_{t}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY macd_{t}m.id DESC
                LIMIT {limit}
            ) AS subquery
            ORDER BY subquery.id ASC
        """.format(t=t, limit=limit // t)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_bollinger_bands(self, symbol, t, limit):
        query = """
            SELECT subquery.*
            FROM (
                SELECT bollingerBands_{t}m.id, bollingerBands_{t}m.signal as bollinger_band
                FROM bollingerBands_{t}m
                JOIN symbols ON bollingerBands_{t}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY bollingerBands_{t}m.id DESC
                LIMIT {limit}
            ) AS subquery
            ORDER BY subquery.id ASC
        """.format(t=t, limit=limit // t)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_super_trend(self, symbol, t, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT superTrend_{t}m.id, superTrend_{t}m.signal as super_trend
                        FROM superTrend_{t}m
                        JOIN symbols ON superTrend_{t}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY superTrend_{t}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(t=t, limit=limit // t)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_rsi(self, symbol, t, limit):
        query = """
                    SELECT subquery.*
                    FROM (
                        SELECT rsi_{t}m.id, rsi_{t}m.signal as rsi
                        FROM rsi_{t}m
                        JOIN symbols ON rsi_{t}m.symbol_id = symbols.id
                        WHERE symbols.symbolName = ?
                        ORDER BY rsi_{t}m.id DESC
                        LIMIT {limit}
                    ) AS subquery
                    ORDER BY subquery.id ASC""".format(t=t, limit=limit // t)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop('id', axis=1)
        return data

    def get_all_indicators(self, symbol, t, limit):

        df1 = self.get_crypto_candle(symbol, t, limit)
        df2 = self.get_moving_average(symbol, t, limit)
        df3 = self.get_macd(symbol, t, limit)
        df4 = self.get_bollinger_bands(symbol, t, limit)
        df5 = self.get_super_trend(symbol, t, limit)
        df6 = self.get_rsi(symbol, t, limit)

        data = pd.concat([df1, df2, df3, df4, df5, df6], axis=1)

        return data


if __name__ == "__main__":
    db_frame = GetDbDataframe()
    data = db_frame.get_minute_data("BTCBUSD", 1, 20)
    print(data[:100])
    indicator = db_frame.get_all_indicators("BTCBUSD", 1, 20)
    print(indicator[:100])