import os
import sqlite3

from all_variable import Variable
# Set database path from Variable class
database = Variable.AI_DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")

conn = sqlite3.connect(database)
cursor = conn.cursor()

TAB_NAME = "cryptoCandle_1"  # change to your table

table_info = cursor.execute(f"PRAGMA TABLE_INFO({TAB_NAME})").fetchall()

for column in table_info:
    print(column)

cursor.close()