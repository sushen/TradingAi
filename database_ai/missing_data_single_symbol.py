import os
import sqlite3
import time
from datetime import datetime, timedelta
import pytz
import pandas as pd
from all_variable import Variable

class MissingDataCollection:
    def __init__(self, database=Variable.AI_DATABASE):
        self.StartTime = time.time()
        self.database = database
        self.absolute_database_path = os.path.abspath(database)  # Ensure absolute path
        print(f"Database path: {self.absolute_database_path}")
        print("This Script Start " + time.ctime())

    def grab_missing_1m(self, symbol):
        print("#################################")
        print("Working on 1")

        try:
            connection = sqlite3.connect(self.absolute_database_path)
            cur = connection.cursor()
            cur.execute("SELECT id FROM symbols WHERE symbolName = ?", (symbol,))
            result = cur.fetchone()
            symbol_id = result[0] if result else None

            if not symbol_id:
                print(f"Symbol {symbol} not found in the database.")
                cur.close()
                connection.close()
                return

            extra = 250
            last_db_id, extra_data = self.get_old_db_data(symbol, connection, symbol_id, 1, extra)

            if last_db_id is None or extra_data.empty:
                print(f"No historical data found for {symbol}, skipping...")
                cur.close()
                connection.close()
                return

            start_time = datetime.strptime(extra_data.index[-1], "%Y-%m-%d %H:%M:%S")
            start_time = start_time.replace(tzinfo=pytz.utc)
            start_time += timedelta(minutes=1)
            end_time = datetime.now(pytz.utc)

            # Get New data
            data = self.get_new_data(symbol, start_time, end_time)
            if data is None or data.empty:
                print("No new data retrieved, skipping...")
                cur.close()
                connection.close()
                return

            store_data = StoreData(data, connection, cur, symbol, 1, len(extra_data), extra_data)
            asset_id = np.arange(last_db_id + 1, last_db_id + len(data) + 1)
            self.store_data_in_db(store_data, symbol_id, asset_id)

            connection.commit()
            cur.close()
        except sqlite3.OperationalError as e:
            print(f"Operational error while connecting to the database: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    # Other methods like get_old_db_data, get_new_db_data, store_data_in_db, etc., are assumed to be defined here

if __name__ == "__main__":
    data_collection = MissingDataCollection()
    data_collection.collect_missing_data_single_symbols("BTCUSDT")
