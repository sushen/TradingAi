import gspread


class Connection:
    @staticmethod
    def connect_worksheet(worksheet_name="tracker"):
        gc = gspread.service_account('C:\\Users\\user\\PycharmProjects\\TradingAiDev\\googlesheet\\trade-tracker-372004-ad983b16bb21.json')
        # gc = gspread.service_account('C:\\Users\\user\\PycharmProjects\\TradingAiDevlopment\\googlesheet\\trade-tracker-372004-ad983b16bb21.json')
        # gc = gspread.service_account('trade-tracker-372004-ad983b16bb21.json')
        spreadsheet = gc.open("TradingAi")
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet


# ws = Connection().connect_worksheet()
# group_list = ws.col_values(1)
# print(group_list)
