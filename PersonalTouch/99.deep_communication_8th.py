import random
import sqlite3
import time

from Bots.AllPageBot import AllPageBot
from Pages.MessagePage import MessagePage
from Pages.ProfilePage import ProfilePage

all_page = AllPageBot()

random_message = [
    "Hi, I saw you comment on a python group.",
    "Hi there! I saw you make a comment on a python group.",
    "Hello, I saw your comment on a python group.",
    "Hello there! I saw your comment on a python group."
]

try:
    login = all_page.test_login()
    print(input("Press any Key: "))
except:
    print("You already lodged in")

massage_we_send = 18
profile_life_circle = 16
updated_profile_life_circle_value = 25


''' this is a two parameter function one is database location and one is massage
we will put this in ca class'''


def text_message():
    text = random.choice(random_message)
    print(text)
    return text


''' this parameter function is work when we make parameter for  text_message() and
we will put this in ca class'''


def message_activity():
    time.sleep(1)
    page_title = all_page.driver.title
    # print(page_title)
    # print(len(page_title))
    if page_title != 'Facebook' and len(page_title) > 10:
        massage_button_xpath = ProfilePage.MASSAGE_BUTTON_XPATH
        massage_button_elements = all_page.driver.find_elements_by_xpath(massage_button_xpath)
        if massage_button_elements:
            massage_button_click = all_page.test_massage_button()
            find_massage_writing_aria = all_page.test_massage_writing_aria()

            xpath = MessagePage.MASSAGE_WRITING_ARIA_XPATH
            elements = all_page.driver.find_elements_by_xpath(xpath)
            ''' if there is more than one elements that means more than one chat windows is open
            so we need to close all windows first then start sending message'''
            if len(elements) > 1:
                print(len(elements))
                print("inside multiple if")
                hover_new_massage = all_page.test_hover_new_massage()
                hide_all_massage_box = all_page.test_hide_all_massage_close()
                close_all_massage_box = all_page.test_all_massage_close()
                massage_button_click = all_page.test_massage_button()
                find_massage_writing_aria = all_page.test_massage_writing_aria()

                massage_writing = all_page.test_massage_writing(text_message())
                print(input("This  is not right correct it: "))
                massage_writing = all_page.test_massage_send()
                time.sleep(2)
                close_massage_box = all_page.test_massage_close()
                print("We close multiple chat box")


            else:
                massage_writing = all_page.test_massage_writing(text_message())
                print(input("If you think this massage is not right correct it: "))
                massage_writing = all_page.test_massage_send()
                time.sleep(2)
                close_massage_box = all_page.test_massage_close()
                print("We find single chat box and send message")
        else:
            connection = sqlite3.connect('../miracle.db')
            cursor = connection.cursor()
            cursor.execute(""" UPDATE facebook_profile SET
                                _fk_profile_life_circle = :fk_profile_life_circle
                                WHERE profile_link =:profile_link""",
                           {
                               'fk_profile_life_circle': 5,
                               'profile_link': all_page.driver.current_url
                           })

            connection.commit()
            connection.close()

    else:
        print("We didn't find x path or this profile block us or facebook block this profile")
        # print(input("Press any Key: "))


def update_record(record):
    connection = sqlite3.connect('../miracle.db')
    cursor = connection.cursor()
    cursor.execute(""" UPDATE facebook_profile SET
                        _fk_profile_life_circle = :fk_profile_life_circle
                        WHERE oid =:oid""",
                   {
                       'fk_profile_life_circle': updated_profile_life_circle_value,
                       'oid': record
                   })

    connection.commit()
    connection.close()
    return record


with open('international_student_real_profile.txt') as file:
    lines = file.readlines()
    print("We have to work with " + str(len(lines)) + " link")
    records = lines

    for groupLinkList in lines:
        profile_life_circle_pk = all_page.driver.get(groupLinkList)
        print(groupLinkList + " link")
        time.sleep(5)

        message_activity()
        update_record(profile_life_circle_pk)
        # print(input("Press any Key: "))

    # connection = sqlite3.connect('../miracle.db')
    # cursor = connection.cursor()
    # # cursor.execute("SELECT group_link, oid FROM facebook_group")
    # cursor.execute(f"SELECT profile_link, _fk_profile_life_circle, oid FROM facebook_profile WHERE _fk_profile_life_circle={profile_life_circle}")
    # records = cursor.fetchall()
    # print(records)
    # index = []
    #     for fbProfile in records:
    #         if len(index) <= 15:
    #             index.append(fbProfile)
    #             single_record_tuples = str(records[len(index) - 1])
    #             fb_link = single_record_tuples[2:single_record_tuples.rfind("',")]
    #             profile_life_circle_pk = records[len(index) - 1][2]
    #
    #             # print(single_record_tuples)
    #             # print(fb_link)
    #             # print(profile_life_circle_pk)
    #             all_page.driver.get(fb_link)
    #
    #             message_activity()
    #             update_record(profile_life_circle_pk)
    #
    #         else:
    #             print("We reach the maximum 15 massage spam limits of sending Private Massage")
    #             break

# connection.commit()
# connection.close()

all_page.driver.quit()
