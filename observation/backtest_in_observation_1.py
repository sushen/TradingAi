import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from dataframe.db_dataframe import GetDbDataframe


from all_variable import Variable
# Set database path from Variable class
database = Variable.DATABASE

# Convert to absolute path
absolute_path = os.path.abspath(database)
script_name = os.path.basename(__file__)
print(f"Database path: {absolute_path} and fine name: {script_name} ")


def main():
    # Time Counting
    import time
    start_time = time.time()
    print("Script Start :", time.ctime())

    import pandas as pd

    pd.set_option('mode.chained_assignment', None)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    target_symbol = "BTCUSDT"
    # missing_data = MissingDataCollection(database=database)
    # missing_data.collect_missing_data_single_symbols(target_symbol)
    # Specify symbol directly
    # timeline = 1
    # timelines = [1, 3, 5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
    timelines = [5, 15, 30, 60, 4 * 60, 24 * 60, 7 * 24 * 60]
    lookback = (1440*30)/4
    # lookback = 1440*30*12

    # Initialize an empty list to store DataFrames for each timeline
    all_Sum_data_frames = []
    for timeline in timelines:
        print(f"\nTimeline {timeline} minutes:")
        # Fetch the required symbol's information
        connection = sqlite3.connect(database)
        db_frame = GetDbDataframe(connection)
        data = db_frame.get_minute_data(target_symbol, timeline, lookback)
        df = db_frame.get_all_indicators(target_symbol, timeline, lookback)

        # print(df.head())

        df.index = data.index  # Set the same index for df
        df = df.add_prefix(f"{timeline}_")
        data[f'Sum_{timeline}'] = df.sum(axis=1)
        # Add a column for the column names with non-zero values
        # data[f'Indicators{timeline}'] = df.apply(lambda row: [col for col in df.columns if row[col] != 0],
                                                        # axis=1)
        data[f'IndicatorsAndValues_{timeline}'] = df.apply(
            lambda row: [(col, row[col]) for col in df.columns if row[col] != 0], axis=1)

        # This time series does not matter
        total_sum_values = pd.Series(0, index=pd.DatetimeIndex([]))
        total_sum_values = total_sum_values.add(data[f'Sum_{timeline}'], fill_value=0)


        total_sum_values = total_sum_values.fillna(0).astype(np.int16)
        df.fillna(0, inplace=True)
        data[f'Sum_{timeline}m'] = total_sum_values
        data[f'Close_Price_{timeline}m'] = data['Close']
        data[f'Close_Time_{timeline}m'] = data['CloseTime']
        # data_frame = data[[f'Sum_{timeline}m', f'IndicatorsAndValues_{timeline}']]
        data_frame = data[[f'Close_Time_{timeline}m', f'Close_Price_{timeline}m', f'Sum_{timeline}m']]
        all_Sum_data_frames.append(data_frame)


        # print(data)

        # Time Counting
        import time
        calculation_end_time = time.time()
        print(f"Dataframe timeline {timeline}m calculation End Time: ", calculation_end_time)
        print(f"Dataframe timeline {timeline}m calculation running for " + str(int(calculation_end_time - start_time))+ " Seconds " + str(int((calculation_end_time - start_time) / 60)) + " Minutes.")
        # print(input("Input :"))

    # print(all_Sum_data_frames)

    # Concatenate all the DataFrames from different timelines into one DataFrame
    final_df = pd.concat(all_Sum_data_frames, axis=1)
    # List of columns that contain the sum values (e.g., Sum_1m, Sum_3m, etc.)
    sum_columns = [col for col in final_df.columns if col.startswith('Sum_')]
    # Calculate the total sum for each row by summing the relevant columns
    final_df['Total_Sum'] = final_df[sum_columns].sum(axis=1)

    print(final_df)

    # print(input("Final DF :"))

    # Time Counting
    import time
    calculation_end_time = time.time()
    print("Dataframe calculation End Time: ", calculation_end_time)
    print("Dataframe calculation running for " + str(int((calculation_end_time - start_time) / 60)) + " Minutes.")

    total_sum = 1000

    price_column_names = final_df.columns
    first_price_column_names = price_column_names[1]
    # print(first_price_column_names)

    marker_sizes = np.abs(final_df['Total_Sum']) / 10

    # Assuming you want to plot the Close_Time_1m from the first DataFrame
    plt.plot(final_df[f'{first_price_column_names}'], label='Close Price')

    buy_indices = final_df.index[final_df['Total_Sum'] >= total_sum]
    plt.scatter(buy_indices, final_df[f'{first_price_column_names}'][final_df['Total_Sum'] >= total_sum],
                marker='^', s=marker_sizes[final_df['Total_Sum'] >= total_sum], color='green',
                zorder=3)
    # Add text labels for sum values
    for index in buy_indices:
        plt.text(index, final_df[f'{first_price_column_names}'][index], f'{(final_df["Total_Sum"])[index]}',
                 ha='center', va='bottom', fontsize=8)

    sell_indices = final_df.index[final_df['Total_Sum'] <= -total_sum]
    plt.scatter(sell_indices, final_df[f'{first_price_column_names}'][final_df['Total_Sum'] <= -total_sum],
                marker='v', s=marker_sizes[final_df['Total_Sum'] <= -total_sum], color='red',
                zorder=3)
    for index in sell_indices:
        plt.text(index, final_df[f'{first_price_column_names}'][index], f'{(final_df["Total_Sum"])[index]}',
                 ha='center', va='bottom', fontsize=8)



    # Title, legend, and grid
    plt.title(f"Backtest of {target_symbol}")
    plt.legend()
    plt.grid(True)

    # Display the plot
    plt.show()



main()

