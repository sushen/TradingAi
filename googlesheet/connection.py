import gspread


class Connection:
    @staticmethod
    def connect_worksheet(worksheet_name="PythonFacebookGroupList"):
        gc = gspread.service_account('../studentfindergspreed-aa5ba05c0365.json')
        spreadsheet = gc.open("StudentFinder")
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet


# ws = Connection().connect_worksheet("MarketingMember")
# group_list = ws.col_values(1)
# print(group_list)
