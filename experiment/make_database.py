import sqlite3

# Create a connection to the database
conn = sqlite3.connect('small_crypto_7days.db')

# Create a cursor object to execute SQL commands
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
    print(f"Table {table_name} created or already exists.")


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
        print(f"Column {column_name} added to {table_name} table.")


# Define schemas for tables
table_definitions = {
    # Each table name points to a tuple: (table_schema, dynamic_columns)
    "symbols": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbolName TEXT)''',
        None  # No dynamic columns
    ),
    "asset_1": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, 
            symbol_id INTEGER, Open REAL, High REAL, 
            Low REAL, Close REAL, Volume REAL, Change REAL, 
            CloseTime INTEGER, VolumeBUSD REAL, Trades INTEGER, 
            BuyQuoteVolume REAL, Time TEXT,
            FOREIGN KEY(symbol_id) REFERENCES symbols(id))''',
        [("VolumeUSDT", "REAL")]
    ),
    "cryptoCandle_1": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
            asset_id INTEGER, CDL2CROWS INTEGER, CDL3BLACKCROWS INTEGER, 
            CDL3INSIDE INTEGER, CDL3LINESTRIKE INTEGER, CDL3OUTSIDE INTEGER,
            FOREIGN KEY(symbol_id) REFERENCES symbols(id), 
            FOREIGN KEY(asset_id) REFERENCES asset_1m(id))''',
        None
    ),
    "movingAverage_1": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER,
            asset_id INTEGER, long_golden INTEGER, short_medium INTEGER,
            medium_golden INTEGER, FOREIGN KEY(symbol_id) REFERENCES symbols(id),
            FOREIGN KEY(asset_id) REFERENCES asset_1m(id))''',
        None
    ),
    "macd_1": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER,
            asset_id INTEGER, signal INTEGER,
            FOREIGN KEY(symbol_id) REFERENCES symbols(id),
            FOREIGN KEY(asset_id) REFERENCES asset_1m(id))''',
        None
    ),
    "bollingerBands_1": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER,
            asset_id INTEGER, signal INTEGER,
            FOREIGN KEY(symbol_id) REFERENCES symbols(id),
            FOREIGN KEY(asset_id) REFERENCES asset_1m(id))''',
        None
    ),
    "rsi_1": (
        '''(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER,
            asset_id INTEGER, signal INTEGER,
            FOREIGN KEY(symbol_id) REFERENCES symbols(id),
            FOREIGN KEY(asset_id) REFERENCES asset_1m(id))''',
        None
    ),

}

# Define all additional tables for regenerated data and news
additional_tables = {
    "regeneratedVolume_1m": "(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, asset_id INTEGER, weightedVolume REAL, FOREIGN KEY(symbol_id) REFERENCES symbols(id), FOREIGN KEY(asset_id) REFERENCES asset_1m(id))",
    "regeneratedTrade_1m": "(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, asset_id INTEGER, weightedTrade REAL, FOREIGN KEY(symbol_id) REFERENCES symbols(id), FOREIGN KEY(asset_id) REFERENCES asset_1m(id))",
    "newsData_1m": "(id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, asset_id INTEGER, newsFromTweets TEXT, newsFromOnlinePortal TEXT, FOREIGN KEY(symbol_id) REFERENCES symbols(id), FOREIGN KEY(asset_id) REFERENCES asset_1m(id))",
}

# =========================
# Process Main Tables
# =========================
for table_name, (schema, dynamic_columns) in table_definitions.items():
    # Create the base table
    create_table(table_name, schema, conn, cur)

    # Add dynamic columns, if any
    if dynamic_columns:
        for column, col_type in dynamic_columns:
            add_column_if_missing(table_name, column, col_type, cur)

# =========================
# Additional Tables
# =========================
for table_name in additional_tables.keys():
    table_schema = additional_tables[table_name]
    create_table(table_name, table_schema, conn, cur)

# =========================
# Extend for Multi-Interval Tables (including 3m)
# =========================
time_intervals = [3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
base_table_names = ["cryptoCandle", "movingAverage", "rsi"]
asset_table_names = ["asset"]

# Generate tables dynamically for other intervals
for interval in time_intervals:
    for asset_table in asset_table_names:
        table_name = f"{asset_table}_{interval}"
        table_schema = table_definitions["asset_1"][0]  # Reuse the structure of asset_1m
        create_table(table_name, table_schema, conn, cur)

    for base_table in base_table_names:
        table_name = f"{base_table}_{interval}"
        table_schema = table_definitions[base_table + "_1"][0]  # Reuse structure of the 1m
        create_table(table_name, table_schema, conn, cur)

# Commit the changes and close the database connection
conn.commit()
conn.close()
