import sqlite3
import pandas as pd
import numpy as np
from resample import ResampleData
from indicator.candle_pattern import MakePattern
from indicator.rsi import Rsi
from indicator.moving_average_signal import MovingAverage
from indicator.macd import Macd
from indicator.bollinger_bands import BollingerBand
from indicator.super_trend import SuperTrend


class Resample:
    def __init__(self, data):
        self.data = data
        self.rb = ResampleData()
        self.minute_data = [3, 5, 15, 30]
        self.connection = sqlite3.connect(r"big_crypto.db")

    def create_minute_data(self, s_id, symbol):
        for minute in self.minute_data:
            print(f"{minute} minuit Data")

            ##########################
            # Storing on asset table #
            ##########################
            print("Resampling Asset Table")
            df_ = self.data.rename_axis('Time_index')
            df_['Time'] = df_.index
            rd = ResampleData(symbol)
            asset_data = rd.resample_to_minute(df_, minute)
            asset_data.rename(columns={f'Volume{symbol[:-4]}': "Volume"}, inplace=True)
            symbol_id = np.ones(len(asset_data), dtype=np.int16) * s_id
            asset_data.insert(0, 'symbol_id', symbol_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS asset_{minute}m 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            symbol_id INTEGER, Open REAL, High REAL, 
                            Low REAL, Close INTEGER, Volume REAL, Change REAL, 
                            CloseTime TEXT, VolumeBUSD REAL, Trades INTEGER, 
                            BuyQuoteVolume REAL, Time TEXT, 
                            FOREIGN KEY(symbol_id) REFERENCES symbols(id))'''.format(minute=minute))
            asset_data.to_sql(name=f'asset_{minute}m', con=self.connection, if_exists='append', index=False)

            #################################
            # Storing on cryptoCandle table #
            #################################
            print("Resampling cryptoCandle Table")
            make_pattern = MakePattern()
            pattern = make_pattern.pattern(asset_data)
            asset_id = pd.read_sql(f"SELECT id FROM asset_{minute}m WHERE symbol_id = {s_id}", self.connection)[
                'id'].tolist()
            pattern.insert(0, 'symbol_id', symbol_id)
            pattern.insert(1, 'asset_id', asset_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS cryptoCandle_{minute}m 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_id INTEGER, 
                            asset_id INTEGER, CDL2CROWS INTEGER, CDL3BLACKCROWS INTEGER, 
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
                            FOREIGN KEY(asset_id) REFERENCES asset(id))'''.format(minute=minute))
            pattern.to_sql(name=f'cryptoCandle_{minute}m', con=self.connection, if_exists='append', index=False, )

            ########################
            # Storing on rsi table #
            ########################
            print("Storing data in rsi table")
            rsi = Rsi()
            rsi_data = rsi.create_rsi(asset_data)
            rsi_data = rsi_data["signal"]
            rsi_data = rsi_data.to_frame()
            rsi_data.insert(0, 'symbol_id', symbol_id)
            rsi_data.insert(1, 'asset_id', asset_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS rsi_{minute}m
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              symbol_id INTEGER,
                              asset_id INTEGER,
                              signal INTEGER,
                              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
                              FOREIGN KEY (asset_id) REFERENCES asset(id))'''.format(minute=minute))
            rsi_data.to_sql(name=f'rsi_{minute}m', con=self.connection, if_exists='append', index=False)

            ##################################
            # Storing on movingAverage table #
            ##################################
            print("Storing data in movingAverage table")
            ma = MovingAverage()
            ma_data = ma.create_moving_average(asset_data)
            ma_data = ma_data[
                ['long_golden', 'short_medium', 'short_long', 'short_golden', 'medium_long', 'medium_golden']]
            ma_data.insert(0, 'symbol_id', symbol_id)
            ma_data.insert(1, 'asset_id', asset_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS movingAverage_{minute}m
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              symbol_id INTEGER, asset_id INTEGER,
                              long_golden INTEGER, short_medium INTEGER, short_long INTEGER, short_golden INTEGER,
                              medium_long INTEGER, medium_golden INTEGER,
                              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
                              FOREIGN KEY (asset_id) REFERENCES asset(id))'''.format(minute=minute))
            ma_data.to_sql(name=f'movingAverage_{minute}m', con=self.connection, if_exists='append', index=False)
            #########################
            # Storing on macd table #
            #########################
            print("Storing data in macd table")
            macd = Macd()
            macd_data = macd.create_macd(asset_data)
            macd_data = macd_data['new_signal']
            macd_data = macd_data.to_frame()
            macd_data = macd_data.rename(columns={'new_signal': 'signal'})
            macd_data.insert(0, 'symbol_id', symbol_id)
            macd_data.insert(1, 'asset_id', asset_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS macd_{minute}m
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              symbol_id INTEGER, asset_id INTEGER,
                              signal INTEGER,
                              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
                              FOREIGN KEY (asset_id) REFERENCES asset(id))'''.format(minute=minute))
            macd_data.to_sql(name=f'macd_{minute}m', con=self.connection, if_exists='append', index=False)

            ###################################
            # Storing on bollinger band table #
            ###################################
            print("Storing data in bollinger band table")
            bb = BollingerBand()
            bb_data = bb.create_bollinger_band(asset_data)
            bb_data = bb_data['signal']
            bb_data = bb_data.to_frame()
            bb_data.insert(0, 'symbol_id', symbol_id)
            bb_data.insert(1, 'asset_id', asset_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS bollingerBands_{minute}m
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              symbol_id INTEGER, asset_id INTEGER,
                              signal INTEGER,
                              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
                              FOREIGN KEY (asset_id) REFERENCES asset(id))'''.format(minute=minute))
            bb_data.to_sql(name=f'bollingerBands_{minute}m', con=self.connection, if_exists='append', index=False)
            ################################
            # Storing on super trend table #
            ################################
            print("Storing data in super trend table")
            df = asset_data.copy()
            df = df.iloc[:, 1:7]
            df.rename(columns={'VolumeBTC': 'volume'}, inplace=True)
            df.index = df.index.rename('datetime')
            df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)

            st = SuperTrend()
            st_data = st.create_super_trend(df)
            st_data = st_data['signal']
            st_data = st_data.to_frame()
            st_data.insert(0, 'symbol_id', symbol_id)
            st_data.insert(1, 'asset_id', asset_id)
            with self.connection as con:
                con.execute('''CREATE TABLE IF NOT EXISTS superTrend_{minute}m
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              symbol_id INTEGER, asset_id INTEGER,
                              signal INTEGER,
                              FOREIGN KEY (symbol_id) REFERENCES symbols(id),
                              FOREIGN KEY (asset_id) REFERENCES asset(id))'''.format(minute=minute))
            st_data.to_sql(name=f'superTrend_{minute}m', con=self.connection, if_exists='append', index=False)
