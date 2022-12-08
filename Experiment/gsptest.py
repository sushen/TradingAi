import gspread

gc = gspread.service_account('../../TradingAi/studentfindergspreed-aa5ba05c0365.json')
spreadsheet = gc.open("StudentFinder")
worksheet = spreadsheet.worksheet("PythonFacebookGroupList")

for i in range(20):
    worksheet.update_cell(i+1, 1, f"{i + 100}  url")