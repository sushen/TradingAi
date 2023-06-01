"""
find your google sheet here : https://docs.google.com/spreadsheets/u/0/
"""
import time

from driver.driver import Driver
from googlesheet.connection import Connection
from login.login import Login
from search.keyword_search import SearchKeyword

driver = Driver().driver
driver.get("https://facebook.com")


Login().login(driver)

work_sheet = Connection().connect_worksheet("MachineLearningGroupList")
# Naro List
# work_sheet = Connection().connect_worksheet("NaroList")

group_list = work_sheet.col_values(1)
print(group_list)
# print(input(":"))


def visit_link_list(driver, link_list):
    list_index = []
    for link in link_list:
        list_index.append(link)
        print(f"\n* {len(list_index)} : {link}\n")
        # driver.get(link)
        time.sleep(2)
        driver.implicitly_wait(4)

        SearchKeyword().scrollAndSearchUsingXpath(driver)
        SearchKeyword().searchWordUsingXpath(driver)
        SearchKeyword().searchCommentUsingXpath(driver)

        # print(input("Visit next group :"))

    print(f"\nWe visit {len(link_list)} link")
    return len(link_list)


visit_link_list(driver, group_list)

