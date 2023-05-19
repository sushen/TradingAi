import sqlite3
import pandas as pd
# from datetime import datetime
# from database.future_dataframe import GetFutureDataframe

# Connect to the database
connection = sqlite3.connect("../database/big_crypto.db")

# Define the symbolName you want to query
symbol_id = 1
symbol = "BTCBUSD"

# Execute the SQL query to fetch the last 250 records in ascending order
query = """
SELECT asset_1m.*, symbols.symbolName as symbol
FROM asset_1m
JOIN symbols ON asset_1m.symbol_id = symbols.id
WHERE symbols.id = ? AND asset_1m.Time > ?
"""

# Fetch the query results into a pandas DataFrame
data = pd.read_sql_query(query, connection, params=(symbol_id, "2023-05-13 08:30:00"))
# data = data.drop('id', axis=1)
data = data.drop(['id', 'symbol_id'], axis=1)
data = data.set_index('Time')
change = data.pop("Change")
data.insert(9, 'Change', change)
data.rename(columns={f'Volume': f"Volume{symbol[:-4]}"}, inplace=True)
# data2 = GetFutureDataframe().get_minute_data(symbol, 1, 250)

# Close the database connection
connection.close()

# Print the DataFrame
print(data)
# time = datetime.strptime(data.iloc[-1]['Time'], "%Y-%m-%d %H:%M:%S")
# print(time)
# print(type(time))
# print(data2[:5])
