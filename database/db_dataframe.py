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

    def get_all_indicators(self, symbol, t, limit):
        query = """
            SELECT subquery.*, movingAverage_{t}m.long_golden, movingAverage_{t}m.short_medium,
            movingAverage_{t}m.short_long, movingAverage_{t}m.short_golden, movingAverage_{t}m.medium_long,
            movingAverage_{t}m.medium_golden, macd_{t}m.signal as macd, bollingerBands_{t}m.signal as bollinger_band,
            superTrend_{t}m.signal as super_trend, rsi_{t}m.signal as rsi
            FROM (
                SELECT cryptoCandle_{t}m.*, symbols.id
                FROM cryptoCandle_{t}m
                JOIN symbols ON cryptoCandle_{t}m.symbol_id = symbols.id
                WHERE symbols.symbolName = ?
                ORDER BY cryptoCandle_{t}m.id DESC
                LIMIT {limit}
            ) AS subquery
            JOIN movingAverage_{t}m ON subquery.symbol_id = movingAverage_{t}m.symbol_id
            JOIN macd_{t}m ON subquery.symbol_id = macd_{t}m.symbol_id
            JOIN bollingerBands_{t}m ON subquery.symbol_id = bollingerBands_{t}m.symbol_id
            JOIN superTrend_{t}m ON subquery.symbol_id = superTrend_{t}m.symbol_id
            JOIN rsi_{t}m ON subquery.symbol_id = rsi_{t}m.symbol_id
            ORDER BY subquery.id ASC
        """.format(t=t, limit=limit)
        data = pd.read_sql_query(query, self.connection, params=(symbol,))
        data = data.drop(['id', 'asset_id'], axis=1)

        return data

if __name__ == "__main__":
    db_frame = GetDbDataframe()
    data = db_frame.get_minute_data("BTCBUSD", 1, 1440)
    print(data)
    indicator = db_frame.get_all_indicators("BTCBUSD", 1, 1440)
    print(indicator)