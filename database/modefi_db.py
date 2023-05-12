import sqlite3
import pandas as pd
from resample import ResampleData

connection = sqlite3.connect(r"../database/cripto_one_year.db")
cur = connection.cursor()
database_data = cur.execute("select * from asset order by CloseTime").fetchall()

df = pd.DataFrame(database_data)
df.columns = ['CloseTime', 'Open', 'High', 'Low', 'Close']
df = df.set_index('CloseTime')
df.index = pd.to_datetime(df.index, unit='ms')
print("Original Data")
print(df)

rb = ResampleData()

# minuit data
minute_data = [3, 5, 15, 30]
for minute in minute_data:
    print(f"{minute} minuit Data")
    df_ = rb.resample_to_minute(df, minute)
    df_ = df_.reset_index()
    df_.to_sql(name=f'asset_{minute}m', con=connection, if_exists='replace', index=False)
    print(df_)

# hour data
hour_data = [1, 5]
for hour in hour_data:
    print(f"{hour} minuit Data")
    df_ = rb.resample_to_minute(df, hour)
    df_ = df_.reset_index()
    df_.to_sql(name=f'asset_{hour}h', con=connection, if_exists='replace', index=False)
    print(df_)

# day data
day_data = [1, 7, 30]
for day in day_data:
    print(f"{day} day Data")
    df_ = rb.resample_to_day(df, day)
    df_ = df_.reset_index()
    df_.to_sql(name=f'asset_{day}d', con=connection, if_exists='replace', index=False)
    print(df_)

connection.close()