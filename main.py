import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pytz
import numpy as np
import sqlite3
from dataframe.db_dataframe import GetDbDataframe
from database_small.missing_data_single_symbol import MissingDataCollection
from playsound import playsound

from all_variable import Variable
# Set database path from Variable class
database = Variable.DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")


def main():
    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    target_symbol = "BTCUSDT"
    missing_data = MissingDataCollection(database=database)
    missing_data.collect_missing_data_single_symbols(target_symbol)
    # Specify symbol directly
    # timeline = 1
    timelines = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
    lookback = 1440*30

    # Initialize an empty list to store DataFrames for each timeline
    all_sum_data_frames = []
    for timeline in timelines:
        # print(f"\ntimeline {timeline} :")
        # Fetch the required symbol's information
        connection = sqlite3.connect(database)
        db_frame = GetDbDataframe(connection)
        data = db_frame.get_minute_data(target_symbol, timeline, lookback)
        df = db_frame.get_all_indicators(target_symbol, timeline, lookback)

        df.index = data.index  # Set the same index for df
        df = df.add_prefix(f"{timeline}_")
        data[f'Sum_{timeline}m'] = df.sum(axis=1)
        data[f'IndicatorsAndValues_{timeline}m'] = df.apply(
            lambda row: [(col, row[col]) for col in df.columns if row[col] != 0], axis=1)

        # This time series does not matter
        total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
        total_sum_values = total_sum_values.add(data[f'Sum_{timeline}m'], fill_value=0)


        total_sum_values = total_sum_values.fillna(0).astype(np.int16)
        df.fillna(0, inplace=True)
        data[f'Sum_{timeline}m'] = total_sum_values
        # print(data)

        data_frame = data.tail(1)[['CloseTime', f'Sum_{timeline}m', f'IndicatorsAndValues_{timeline}m']]
        # Convert the 'CloseTime' column to datetime format
        data_frame['CloseTime'] = pd.to_datetime(data_frame['CloseTime'], unit='ms')
        data_frame[f'Time_{timeline}m'] = data['CloseTime']
        data_frame.reset_index(drop=True, inplace=True)
        all_sum_data_frames.append(data_frame)


    # Concatenate all the DataFrames from different timelines into one DataFrame
    final_df = pd.concat(all_sum_data_frames, axis=1)
    # print("Final DataFrame:")
    # print(final_df.tail())

    # Define local timezone
    local_tz = pytz.timezone('Asia/Dhaka')
    time_columns = [col for col in final_df.columns if col.startswith('Time_')]

    for col in time_columns:
        final_df[col] = pd.to_datetime(final_df[col] / 1000, unit='s')
        final_df[col] = final_df[col].dt.tz_localize('UTC').dt.tz_convert(local_tz)

    # print("Full Final DataFrame with Local Time:")
    final_df = final_df.drop([col for col in final_df.columns if 'CloseTime' in col], axis=1)

    # List of columns that contain the sum values (e.g., Sum_1m, Sum_3m, etc.)
    sum_columns = [col for col in final_df.columns if col.startswith('Sum_')]
    # Calculate the total sum for each row by summing the relevant columns
    final_df['Total_Sum'] = final_df[sum_columns].sum(axis=1)
    indicators_columns = [col for col in final_df.columns if 'IndicatorsAndValues' in col]
    final_df['Total_IndicatorsAndValues'] = final_df[indicators_columns].apply(lambda row: sum(row.tolist(), []),
                                                                               axis=1)
    # Print the DataFrame with the Total_Sum column added
    # print("DataFrame with Total_Sum added:")
    # print(final_df)
    # print(final_df["Total_Sum"])
    # print(final_df["Total_IndicatorsAndValues"])

    signal_sum = final_df["Total_Sum"]
    # print(f"Normal Signal Sum: {signal_sum.iloc[0]}")
    signal_indicators = final_df["Total_IndicatorsAndValues"]
    # print(f"This minutes Indicators:{signal_indicators.iloc[0]}")


    total_sum = 1300

    # Filter the rows where the condition is true
    buy_indices = final_df[final_df["Total_Sum"] >= total_sum]

    # Check if there are any rows matching the condition
    if not buy_indices.empty:
        # Create a dictionary to store signals by their timeline
        timelines_dictionary = {timeline: [] for timeline in timelines}

        # Categorize the signals by their timeline
        for indicators in final_df["Total_IndicatorsAndValues"]:
            for signal, value in indicators:  # Now, iterate over the unpacked tuples
                timeline = int(signal.split('_')[0])  # Extract the timeline (e.g., 1, 3, 5, etc.)
                if timeline in timelines_dictionary:
                    timelines_dictionary[timeline].append((signal, value))

        # Create the email body in plain text format
        email_body = f"Dear User,\n\nThe current signals:{signal_sum.iloc[0]} \n\n"

        for timeline, timeline_signals in timelines_dictionary.items():
            if timeline_signals:  # Only add the section if there are signals for this timeline
                email_body += f"Timeline: {timeline} minutes\n"
                for signal, value in timeline_signals:
                    email_body += f"- {signal}: {value}\n"
                email_body += "\n"  # Add a newline after each timeline section

        email_body += f"Signal {signal_sum.iloc[0]}\nBest regards,\nMango Trading System \n................\n\n\n"

        # Print or use the email body
        print(email_body)

        # Discord Message Functionality
        from discord_bot.discord_message import Messages
        messages = Messages()
        messages.send_massage(email_body)

        print("The Bullish sound")
        playsound(r'sounds/Bullish.wav')

    # Similarly for sell indices
    sell_indices = final_df[final_df["Total_Sum"] <= -total_sum]
    if not sell_indices.empty:
        # Create a dictionary to store signals by their timeline
        timelines_dictionary = {timeline: [] for timeline in timelines}

        # Categorize the signals by their timeline
        for indicators in final_df["Total_IndicatorsAndValues"]:
            for signal, value in indicators:  # Now, iterate over the unpacked tuples
                timeline = int(signal.split('_')[0])  # Extract the timeline (e.g., 1, 3, 5, etc.)
                if timeline in timelines_dictionary:
                    timelines_dictionary[timeline].append((signal, value))

        # Create the email body in plain text format
        email_body = "Dear User,\n\nHere are the current signals:\n\n"

        for timeline, timeline_signals in timelines_dictionary.items():
            if timeline_signals:  # Only add the section if there are signals for this timeline
                email_body += f"Timeline: {timeline} minutes\n"
                for signal, value in timeline_signals:
                    email_body += f"- {signal}: {value}\n"
                email_body += "\n"  # Add a newline after each timeline section

        email_body += f"Signal {signal_sum.iloc[0]}\nBest regards,\nMango Trading System \n................\n\n\n"

        # Discord Message Functionality
        from discord_bot.discord_message import Messages
        messages = Messages()
        messages.send_massage(email_body)

        # Print or use the email body
        print(email_body)

        print("The Bearish sound")
        playsound(r'./sounds/Bearish.wav')

    # EndTime = time.time()
    # print("\nThis Script End " + time.ctime())
    # totalRunningTime = EndTime - StartTime
    # print("This Script is running " + str(int(totalRunningTime)) + " Seconds.")

StartTime = time.time()
while True:
    StartLoopTime = time.time()

    main()

    LoopEndTime = time.time()
    totalLoopRunningTime = LoopEndTime - StartLoopTime
    print(f"Main Calculation need {totalLoopRunningTime} seconds.")

    sleep_time = 60 - totalLoopRunningTime
    time.sleep(abs(sleep_time))
    EndTime = time.time()
    totalRunningTime = EndTime - StartTime
    print("\nThis Script is running " + str(int(totalRunningTime)/60) + " minutes.\n")

