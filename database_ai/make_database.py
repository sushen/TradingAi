"""
Script Name: make_database.py
Author: Sushen Biswas
Date: @2023-10-30
Last Update: 2024-03-10
"""

import sqlite3
import os
import logging
from all_variable import Variable

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Get the absolute database path
database = os.path.abspath(Variable.AI_DATABASE)
absolute_path = os.path.abspath(database)
logger.info(f"Database path: {absolute_path} and script name: {os.path.basename(__file__)}")

# Establish database connection
try:
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    logger.info("Connected to the database successfully.")
except sqlite3.Error as e:
    logger.error(f"Failed to connect to the database: {e}")
    exit(1)

# Function to create tables
def create_table(table_name, schema, connection, cursor):
    try:
        create_query = f'''CREATE TABLE IF NOT EXISTS {table_name} {schema}'''
        cursor.execute(create_query)
        connection.commit()
        logger.info(f"Table {table_name} created or already exists.")
    except sqlite3.Error as e:
        logger.error(f"Error creating table {table_name}: {e}")

# Function to add missing columns
def add_column_if_missing(table_name, column_name, column_type, cursor):
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
            logger.info(f"Column {column_name} added to {table_name}.")
    except sqlite3.Error as e:
        logger.error(f"Error adding column {column_name} to {table_name}: {e}")

# Function to add indexing for optimization
def add_index_for_time(table_name, cursor):
    try:
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_time_{table_name} ON {table_name} (Time_unix);")
        logger.info(f"Index created for Time_unix in {table_name}.")
    except sqlite3.Error as e:
        logger.error(f"Error creating index for Time_unix in {table_name}: {e}")

def add_index_for_foreign_keys(table_name, cursor):
    try:
        cursor.execute("PRAGMA foreign_keys=off;")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_symbol_{table_name} ON {table_name} (symbol_id);")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_asset_{table_name} ON {table_name} (asset_id);")
        cursor.execute("PRAGMA foreign_keys=on;")
        logger.info(f"Foreign key indexes created in {table_name}.")
    except sqlite3.Error as e:
        logger.error(f"Error creating foreign key indexes in {table_name}: {e}")

# Table definitions
table_definitions = {
    "symbols": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbolName TEXT)''',
    "asset": '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     symbol_id INTEGER, Open REAL, High REAL, 
                     Low REAL, Close REAL, VolumeBTC REAL,  
                     CloseTime INTEGER, VolumeUSDT REAL, Trades INTEGER,
                     BuyQuoteVolume REAL, Change REAL, Time TEXT,
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
time_intervals = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]  # 1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d, 7d

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

# Create main tables
for table_name, schema in table_definitions.items():
    create_table(table_name, schema, conn, cur)
    add_column_if_missing(table_name, "Time_unix", "INTEGER", cur)
    add_column_if_missing(table_name, "symbol_id", "INTEGER", cur)
    add_column_if_missing(table_name, "asset_id", "INTEGER", cur)
    add_index_for_time(table_name, cur)
    add_index_for_foreign_keys(table_name, cur)

# Create interval-based tables dynamically
for interval in time_intervals:
    for base_table in base_table_names:
        table_name = f"{base_table}_{interval}"
        table_schema = table_definitions[base_table]
        create_table(table_name, table_schema, conn, cur)
        add_column_if_missing(table_name, "Time_unix", "INTEGER", cur)
        add_column_if_missing(table_name, "symbol_id", "INTEGER", cur)
        add_column_if_missing(table_name, "asset_id", "INTEGER", cur)
        add_index_for_time(table_name, cur)
        add_index_for_foreign_keys(table_name, cur)

# Commit changes and close connection
try:
    conn.commit()
    logger.info("[INFO] Database setup complete.")
except sqlite3.Error as e:
    logger.error(f"Error committing changes to the database: {e}")

conn.close()
