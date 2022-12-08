from googlesheet.connection import Connection

work_sheet = Connection().connect_worksheet("BanglaStudent")

group_list = work_sheet.col_values(1)


from datetime import datetime


for i in range(len(group_list)):

    current_unix_time = int(datetime.now().timestamp())
    # print(current_unix_time)
    # print(datetime.fromtimestamp(current_unix_time).strftime('%Y-%m-%d %H:%M:%S'))

    total_second_in_day = 60 * 60 * 24
    # print(total_second_in_day)

    day_early_time = current_unix_time - total_second_in_day
    # print(day_early_time)

    print(datetime.fromtimestamp(day_early_time).strftime('%Y-%m-%d %H:%M:%S'))

    cell_value = work_sheet.cell(i+1, 3).value
    print(cell_value)

    if cell_value is None:
        work_sheet.update_cell(i+1, 3, int(datetime.now().timestamp()))
    elif (int(cell_value) + total_second_in_day) < current_unix_time:
        print(current_unix_time-int(cell_value))

    print(input("Stop: "))




