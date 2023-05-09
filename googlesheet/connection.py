import gspread


class Connection:
    @staticmethod
    def connect_worksheet(worksheet_name="PythonFacebookGroupList"):
        gc = gspread.service_account('trade-tracker-372004-ad983b16bb21.json')
        spreadsheet = gc.open("TradingAi")
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet


if __name__ == '__main__':
    ws = Connection().connect_worksheet("communication")
    group_list = ws.col_values(1)
    print(group_list)
