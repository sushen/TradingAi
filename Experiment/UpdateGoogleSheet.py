from googlesheet.connection import Connection

work_sheet = Connection().connect_worksheet("BanglaStudent")

group_list = work_sheet.col_values(1)
# print(group_list)

for i in range(len(group_list)):
    # print(len(group_list))
    print(i)
    sell_Value = work_sheet.row_values(i+1)
    print(sell_Value)
    work_sheet.update_cell(i+1, 2, 1)
