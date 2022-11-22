import sqlite3
import time

from dataframe import GetDataframe

while True:
    # time.sleep(10)

    symbol = 'BTCBUSD'
    api_data = GetDataframe().get_minute_data(symbol, 1, 1)
    print(api_data['CloseTime'][0])

    connection = sqlite3.connect("cripto.db")
    cur = connection.cursor()
    database_data = cur.execute("select CloseTime from asset order by CloseTime desc limit 1").fetchone()[0]

    print(database_data)

    print(input("Stop :"))

    # TODO : Logic for Writing New Database
    if api_data['CloseTime'][0] != database_data:
        open_position = api_data['Open'].iloc[0]
        high_position = api_data['High'].iloc[0]
        low_position = api_data['Low'].iloc[0]
        close_position = api_data['Close'].iloc[0]

        symbol_volume_position = api_data[f'Volume{symbol[:-4]}'].iloc[0]
        close_time = api_data['CloseTime'].iloc[0]
        trades = api_data['Trades'].iloc[0]
        buy_quote_volume = api_data['BuyQuoteVolume'].iloc[0]

        change_position = api_data['Change'].iloc[0]
        symbol_position = api_data['symbol'].iloc[0]
        time_position = api_data.index[0]
        unix_time = time_position.timestamp()
        print(
            f"{open_position}, {high_position}, {low_position}, {close_position}, {symbol_volume_position}, {change_position}, {symbol_position} , {time_position}, {unix_time}")

        cur.execute(
            "INSERT INTO asset VALUES (:id, :symbol, :Open, :High, :Low,  :Close, :VolumeBTC, :Change , :Time , :CloseTime, :Trades, :BuyQuoteVolume )",
            {
                'id': None,
                'symbol': symbol,
                'Open': open_position,
                'High': high_position,
                'Low': low_position,
                'Close': close_position,
                'VolumeBTC': symbol_volume_position,
                'Change': change_position,
                'CloseTime': close_time,
                'Trades': trades,
                'BuyQuoteVolume': buy_quote_volume,
                'Time': unix_time
            })
        connection.commit()
        cur.close()
    else:
        print("Waiting for new data")
