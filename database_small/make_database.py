"""
Script Name: make_database.py
Author: Sushen Biswas
Date: @2023-10-30
Last Update: 2023-10-30 15:30:00
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from all_variable import Variable
# Set database path from Variable class
database = Variable.DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")

# Create a connection to the database
conn = sqlite3.connect(database)  # Adjust database file name if needed
cur = conn.cursor()


# Function to create tables dynamically
def create_table(table_name, schema, connection, cursor):
    """
    Create a table if it does not exist.
    :param table_name: Name of the table to create.
    :param schema: Schema of the table as a SQL CREATE TABLE query.
    :param connection: Active SQLite database connection.
    :param cursor: Cursor object to execute SQL queries.
    """
    create_query = f'''CREATE TABLE IF NOT EXISTS {table_name} {schema}'''
    cursor.execute(create_query)
    connection.commit()
    print(f"[INFO] Table {table_name} created or already exists.")


# Function to check if a column exists and add it dynamically
def add_column_if_missing(table_name, column_name, column_type, cursor):
    """
    Check for a column in the table and add it if missing.
    :param table_name: Name of the table.
    :param column_name: Name of the column.
    :param column_type: Data type of the column.
    :param cursor: Cursor object to perform operations.
    """
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        print(f"[INFO] Column {column_name} added to {table_name} table.")


# Define table schemas
table_definitions = {
    # Base tables
    "symbols": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbolName TEXT)''',
    "asset": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 symbol_id INTEGER, Open REAL, High REAL, 
                 Low REAL, Close REAL, VolumeBTC REAL, Change REAL, 
                 CloseTime INTEGER, Trades INTEGER, 
                 BuyQuoteVolume REAL, VolumeUSDT REAL, Time TEXT,
                 FOREIGN KEY(symbol_id) REFERENCES symbols(id))''',
    "cryptoCandle": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
                        asset_id INTEGER, CDL2CROWS INTEGER, CDL3BLACKCROWS INTEGER, 
                        CDL3INSIDE INTEGER, CDL3LINESTRIKE INTEGER, CDL3OUTSIDE INTEGER, 
                        CDL3STARSINSOUTH INTEGER, CDL3WHITESOLDIERS INTEGER, 
                        CDLABANDONEDBABY INTEGER, CDLADVANCEBLOCK INTEGER, 
                        CDLBELTHOLD INTEGER, CDLBREAKAWAY INTEGER, 
                        CDLCLOSINGMARUBOZU INTEGER, CDLCONCEALBABYSWALL INTEGER, 
                        CDLCOUNTERATTACK INTEGER, CDLDARKCLOUDCOVER INTEGER, 
                        CDLDOJI INTEGER, CDLDOJISTAR INTEGER, CDLDRAGONFLYDOJI INTEGER, 
                        CDLENGULFING INTEGER, CDLEVENINGDOJISTAR INTEGER, 
                        CDLEVENINGSTAR INTEGER, CDLGAPSIDESIDEWHITE INTEGER, 
                        CDLGRAVESTONEDOJI INTEGER, CDLHAMMER INTEGER, 
                        CDLHANGINGMAN INTEGER, CDLHARAMI INTEGER, CDLHARAMICROSS INTEGER, 
                        CDLHIGHWAVE INTEGER, CDLHIKKAKE INTEGER, CDLHIKKAKEMOD INTEGER, 
                        CDLHOMINGPIGEON INTEGER, CDLIDENTICAL3CROWS INTEGER, CDLINNECK INTEGER, 
                        CDLINVERTEDHAMMER INTEGER, CDLKICKING INTEGER, 
                        CDLKICKINGBYLENGTH INTEGER, CDLLADDERBOTTOM INTEGER, 
                        CDLLONGLEGGEDDOJI INTEGER, CDLLONGLINE INTEGER, CDLMARUBOZU INTEGER, 
                        CDLMATCHINGLOW INTEGER, CDLMATHOLD INTEGER, CDLMORNINGDOJISTAR INTEGER, 
                        CDLMORNINGSTAR INTEGER, CDLONNECK INTEGER, CDLPIERCING INTEGER, 
                        CDLRICKSHAWMAN INTEGER, CDLRISEFALL3METHODS INTEGER, CDLSEPARATINGLINES INTEGER, 
                        CDLSHOOTINGSTAR INTEGER, CDLSHORTLINE INTEGER, CDLSPINNINGTOP INTEGER, 
                        CDLSTALLEDPATTERN INTEGER, CDLSTICKSANDWICH INTEGER, CDLTAKURI INTEGER, 
                        CDLTASUKIGAP INTEGER, CDLTHRUSTING INTEGER, CDLTRISTAR INTEGER, 
                        CDLUNIQUE3RIVER INTEGER, CDLUPSIDEGAP2CROWS INTEGER, 
                        CDLXSIDEGAP3METHODS INTEGER, FOREIGN KEY(symbol_id) REFERENCES symbols(id), 
                        FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "movingAverage": '''(id INTEGER PRIMARY KEY AUTOINCREMENT,
                         symbol_id INTEGER, asset_id INTEGER, long_golden INTEGER, 
                         short_medium INTEGER, short_long INTEGER, short_golden INTEGER,
                         medium_long INTEGER, medium_golden INTEGER,
                         FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                         FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "macd": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
                asset_id INTEGER, signal INTEGER,
                FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "bollingerBands": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
                          asset_id INTEGER, signal INTEGER,
                          FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                          FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "superTrend": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
                      asset_id INTEGER, signal INTEGER,
                      FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                      FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "rsi": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
               symbol_id INTEGER, asset_id INTEGER, signal INTEGER,
               FOREIGN KEY(symbol_id) REFERENCES symbols(id),
               FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "newsData": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    symbol_id INTEGER, asset_id INTEGER, 
                    newsFromTweets TEXT, newsFromOnlinePortal TEXT, 
                    newsFromConference TEXT, tvNews TEXT, 
                    facebookViralNews TEXT,
                    FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                    FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "calendarData": '''(id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol_id INTEGER, asset_id INTEGER, 
                        Amavasya TEXT, Purnima TEXT, "Durga Puja" TEXT, 
                        Eid_Ul_Fitr TEXT, Eid_Ul_Adha TEXT,
                        FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                        FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "regeneratedVolume": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                              symbol_id INTEGER, asset_id INTEGER, weightedVolume REAL,
                              FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                              FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "regeneratedTrade": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             symbol_id INTEGER, asset_id INTEGER, weightedTrade REAL,
                             FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                             FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "regeneratedChanges": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               symbol_id INTEGER, asset_id INTEGER, weightedChanges REAL,
                               FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                               FOREIGN KEY(asset_id) REFERENCES asset(id))''',
    "regeneratedBuyQuote": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                symbol_id INTEGER, asset_id INTEGER, weightedBuyQuote REAL,
                                FOREIGN KEY(symbol_id) REFERENCES symbols(id),
                                FOREIGN KEY(asset_id) REFERENCES asset(id))''',
}

# Time intervals
time_intervals = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]

# Base table names (interval-based)
base_table_names = [
    "asset",
    "cryptoCandle",
    "movingAverage",
    "macd",
    "bollingerBands",
    "superTrend",
    "rsi",
    "regeneratedVolume",
    "regeneratedTrade",
    "regeneratedChanges",
    "regeneratedBuyQuote",
    "newsData",
    "calendarData",
]

# Create tables without intervals
for table_name, schema in table_definitions.items():
    create_table(table_name, schema, conn, cur)

# Create interval-based tables dynamically
for interval in time_intervals:
    for base_table in base_table_names:
        table_name = f"{base_table}_{interval}"
        table_schema = table_definitions[base_table]
        create_table(table_name, table_schema, conn, cur)

# Commit changes and close connection
conn.commit()
conn.close()