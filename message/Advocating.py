"""
We test our advocacy in this page : https://www.facebook.com/groups/341334433330410/permalink/1266678044129373/
"""
import random

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from message.message_text import MessageText
from datetime import datetime
import time
from driver.driver import Driver
from googlesheet.connection import Connection
from login.login import Login
import re

general_question_start = "I like to know couple answer like : "

# Mahmuds cmment
massage_list = ["Are you using broadband internet ?",
                "Are you using a PC for programming?",
                "What is your PC configuration ?",
                "What is your timezone?"]

general_question_end = " Would you like to make the conversation."

# massage_list = ["আপনি অংক আর পাইথন শিখতে পাড়েন ।",
#                 "আমার কিছু প্রশ্ন ছিল । যেমন: কি ব্যাকগ্রাইন্ড থেকে আপনি এসেছেন ?  ",
#                 "আমার কিছু প্রশ্ন ছিল । যেমন: শেখার জন্য নির বিচ্ছিন্ন ভিডিওকলে থাকতে পাড়বেন কিনা ?",
#                 "আমার কিছু প্রশ্ন ছিল । যেমন: আপনি কখনও হ্যালো লিখেছেন কিন ?"]

# message = random.choice(massage_list)
# print(message)

# print(input("Testing Message :"))
# TODO : find Tanjil Hosain Kabbo and like his comment and make a encouraging reply in his post
# group_link = "https://www.facebook.com/groups/python/permalink/1289109118596316/"

group_link = "https://www.facebook.com/groups/DataScienceGroup/permalink/3595283820533482/"

driver = Driver().driver
action = ActionChains(driver)
driver.get("https://facebook.com")


Login().login(driver)

driver.get(group_link)

# print(input("Find Top comments :"))


def find_top_comment():
    driver.implicitly_wait(4)
    if driver.find_elements(By.XPATH, "//span[contains(.,'Top comments')]"):
        top_comments = driver.find_element(By.XPATH, "//span[contains(.,'Top comments')]")
        print(top_comments)
        top_comments.click()


def find_all_comment():
    driver.implicitly_wait(4)
    if driver.find_elements(By.XPATH, "//span[normalize-space()='All comments']"):
        all_comments = driver.find_element(By.XPATH, "//span[normalize-space()='All comments']")
        print(all_comments)
        all_comments.click()


def find_previous_comment():
    driver.implicitly_wait(4)
    if driver.find_elements(By.XPATH, "//span[contains(text(),'previous comments')]"):
        previous_comments = driver.find_element(By.XPATH, "//span[contains(text(),'previous comments')]")
        # print(previous_comments)
        print("We are searching previous comment")
        previous_comments.click()


find_top_comment()
find_all_comment()

while True:
    time.sleep(2)
    driver.implicitly_wait(1)
    if driver.find_elements(By.XPATH, "//span[contains(text(),'previous comments')]"):
        find_previous_comment()
    else:
        break

# print(input("Stop :"))

time.sleep(5)
driver.implicitly_wait(10)
main_comments = driver.find_elements(By.XPATH, "//div[@role='article']")
print(len(main_comments))

main_comments_reply_button = driver.find_elements(By.XPATH, "//div[@role='button'][normalize-space()='Reply']")
print(len(main_comments_reply_button))

comment_index = []
for comment in main_comments:
    comment_index.append(comment)
    print(f"Index : {len(comment_index)}")

    # TODO: We can implement a natural language processor here
    print(comment.text)
    # Base on regular expression create condition
    index = []
    for m in re.finditer(r"\binterested\b", comment.text):
        if m.group(0):
            index.append(m)
            print("Present")

    if len(index) != 0:
        # print("Total " + str(len(index)) + " 'interested' Word Found")
        print(f"We are replaying {len(comment_index)} comment")
        action.move_to_element(comment).click(comment).perform()
        main_comments_reply_button[len(comment_index) - 1].click()
        action.send_keys(general_question_start + random.choice(massage_list) + general_question_end).send_keys(Keys.ENTER).perform()
        # time.sleep(4)
        print(input("Press any Key: "))
    else:
        print("No 'interested' Word Found")

    print("......................")

print(input("Comment Done :"))

