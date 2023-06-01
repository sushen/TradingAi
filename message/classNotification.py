from selenium.webdriver.common.by import By

import time

from driver.driver import Driver
from googlesheet.connection import Connection
from login.login import Login


message = "previous link not working this was work fine. https://www.youtube.com/watch?v=ps446KNJjac , if you available now"
# message = "I am teaching crypto price prediction using ML if that is something you want to learn let me know.  https://youtu.be/Al4g8whYsNw"

print(message)


driver = Driver().driver
driver.get("https://facebook.com")


Login().login(driver)

"""
Documentation :
https://docs.gspread.org/en/v5.4.0/oauth2.html#oauth-client-id          
"""

work_sheet = Connection().connect_worksheet("MachineLearningStudent")
group_list = work_sheet.col_values(1)
# print(group_list)


def send_message():

    driver.find_element(By.XPATH, "//span[contains(text(),'Message')]").click()
    driver.implicitly_wait(10)
    time.sleep(2)
    driver.find_element(By.XPATH, "//p[@class='xat24cr xdj266r']").send_keys(message)
    # print(input("Stop :"))
    driver.find_element(By.XPATH, "//div[@aria-label='Press enter to send']//*[name()='svg']").click()
    time.sleep(4)

    driver.find_element(By.XPATH, "//div[@aria-label='Close chat']").click()


def visit_link_list(driver, link_list):
    list_index = []
    for i in range(len(link_list)):
        list_index.append(link_list[i])
        print(f"\n* {len(list_index)} : {link_list[i]}\n")
        driver.get(link_list[i])
        time.sleep(2)
        driver.implicitly_wait(4)

        send_message()

        # print(input("Message Next Person:"))

    print(f"\nWe visit {len(link_list)} link")
    return len(link_list)


visit_link_list(driver, group_list)

