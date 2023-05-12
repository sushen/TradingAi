import sqlite3

# create a connection to the database
conn = sqlite3.connect('big_crypto.db')

# create a cursor object to execute SQL commands
cur = conn.cursor()

# Table 1: symbols
cur.execute('''CREATE TABLE IF NOT EXISTS symbols 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, symbolName TEXT)''')

# Table 2: asset
cur.execute('''CREATE TABLE IF NOT EXISTS asset 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            symbol_id INTEGER, Open REAL, High REAL, 
            Low REAL, Close REAL, Volume REAL, Change REAL, 
            CloseTime TEXT, VolumeBUSD REAL, Trades INTEGER, 
            BuyQuoteVolume REAL, Time TEXT, 
            FOREIGN KEY(symbol_id) REFERENCES symbols(id))''')

# Table 3: cryptoCandle
cur.execute('''CREATE TABLE IF NOT EXISTS cryptoCandle 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
            crypto_id INTEGER, CDL2CROWS INTEGER, CDL3BLACKCROWS INTEGER, 
            CDL3INSIDE INTEGER, CDL3LINESTRIKE INTEGER, CDL3OUTSIDE INTEGER, 
            CDL3STARSINSOUTH INTEGER, CDL3WHITESOLDIERS INTEGER, 
            CDLABANDONEDBABY INTEGER, CDLADVANCEBLOCK INTEGER, 
            CDLBELTHOLD INTEGER, CDLBREAKAWAY INTEGER, 
            CDLCLOSINGMARUBOZU INTEGER, CDLCONCEALBABYSWALL INTEGER, 
            CDLCOUNTERATTACK INTEGER, CDLDARKCLOUDCOVER INTEGER, CDLDOJI INTEGER,
            CDLDOJISTAR INTEGER, CDLDRAGONFLYDOJI INTEGER, CDLENGULFING INTEGER, 
            CDLEVENINGDOJISTAR INTEGER, CDLEVENINGSTAR INTEGER, 
            CDLGAPSIDESIDEWHITE INTEGER, CDLGRAVESTONEDOJI INTEGER, 
            CDLHAMMER INTEGER, CDLHANGINGMAN INTEGER, CDLHARAMI INTEGER, 
            CDLHARAMICROSS INTEGER, CDLHIGHWAVE INTEGER, CDLHIKKAKE INTEGER, 
            CDLHIKKAKEMOD INTEGER, CDLHOMINGPIGEON INTEGER, CDLIDENTICAL3CROWS INTEGER, 
            CDLINNECK INTEGER, CDLINVERTEDHAMMER INTEGER, CDLKICKING INTEGER, 
            CDLKICKINGBYLENGTH INTEGER, CDLLADDERBOTTOM INTEGER, 
            CDLLONGLEGGEDDOJI INTEGER, CDLLONGLINE INTEGER, CDLMARUBOZU INTEGER, 
            CDLMATCHINGLOW INTEGER, CDLMATHOLD INTEGER, CDLMORNINGDOJISTAR INTEGER, 
            CDLMORNINGSTAR INTEGER, CDLONNECK INTEGER, CDLPIERCING INTEGER, 
            CDLRICKSHAWMAN INTEGER, CDLRISEFALL3METHODS INTEGER, CDLSEPARATINGLINES INTEGER, 
            CDLSHOOTINGSTAR INTEGER, CDLSHORTLINE INTEGER, CDLSPINNINGTOP INTEGER, 
            CDLSTALLEDPATTERN INTEGER, CDLSTICKSANDWICH INTEGER, CDLTAKURI INTEGER, 
            CDLTASUKIGAP INTEGER, CDLTHRUSTING INTEGER, 
            CDLTRISTAR INTEGER, CDLUNIQUE3RIVER INTEGER, 
            CDLUPSIDEGAP2CROWS INTEGER, CDLXSIDEGAP3METHODS INTEGER, 
            FOREIGN KEY(symbol_id) REFERENCES symbols(id), 
            FOREIGN KEY(crypto_id) REFERENCES asset(id))''')

# Table 4: movingAverage
cur.execute('''CREATE TABLE IF NOT EXISTS movingAverage
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER, crypto_id INTEGER,
              long_golden INTEGER, short_medium INTEGER, short_long INTEGER, short_golden INTEGER,
              medium_long INTEGER, medium_golden INTEGER,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table : MACD
cur.execute('''CREATE TABLE IF NOT EXISTS macd
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER, crypto_id INTEGER,
              signal INTEGER,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 5: bollingerBands
cur.execute('''CREATE TABLE IF NOT EXISTS bollingerBands
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER, crypto_id INTEGER,
              signal INTEGER,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 6: superTrend
cur.execute('''CREATE TABLE IF NOT EXISTS superTrend
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER, crypto_id INTEGER,
              signal INTEGER,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 7: rsi
cur.execute('''CREATE TABLE IF NOT EXISTS rsi
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER,
              crypto_id INTEGER,
              signal INTEGER,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 8: regeneratedVolume
cur.execute('''CREATE TABLE IF NOT EXISTS regeneratedVolume
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER,
              crypto_id INTEGER,
              weightedVolume REAL,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 9: regeneratedTrade
cur.execute('''CREATE TABLE IF NOT EXISTS regeneratedTrade
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER,
              crypto_id INTEGER,
              weightedTrade REAL,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 10: regeneratedChanges
cur.execute('''CREATE TABLE IF NOT EXISTS regeneratedChanges
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER,
              crypto_id INTEGER,
              weightedChanges REAL,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 11: regeneratedBuyQuote
cur.execute('''CREATE TABLE IF NOT EXISTS regeneratedBuyQuote
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER,
              crypto_id INTEGER,
              weightedBuyQuote REAL,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# Table 12: newsData
cur.execute('''CREATE TABLE IF NOT EXISTS newsData
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              symbol_id INTEGER,
              crypto_id INTEGER,
              newsFromTweets TEXT,
              newsFromOnlinePortal TEXT,
              newsFromConference TEXT,
              tvNews TEXT,
              facebookViralNews TEXT,
              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
              FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# create table 13 - calendarData
cur.execute('''CREATE TABLE IF NOT EXISTS calendarData
             (id INTEGER PRIMARY KEY,
             symbol_id INTEGER,
             crypto_id INTEGER,
             Amavasya TEXT,
             Purnima TEXT,
             "Durga Puja" TEXT,
             Eid_Ul_Fitr TEXT,
             Eid_Ul_Adha TEXT,
             FOREIGN KEY (symbol_id) REFERENCES symbols(id),
             FOREIGN KEY (crypto_id) REFERENCES asset(id))''')

# commit the changes and close the connection
conn.commit()
conn.close()
