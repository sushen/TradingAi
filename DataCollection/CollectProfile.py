import time
import pyperclip as pc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from Bots.bot_LoginPage import Bot_Login

login = Bot_Login()
wait_time = 30

try:
    fb_login = login.test_login()
    print(input("Press any Key: "))
except:
    print(" You already lodged in")


def switch_browser_tab():
    window_before = login.driver.window_handles[0]
    print("Group Window :" + window_before)

    window_after = login.driver.window_handles[1]
    print("Single Group Link Window :" + window_after)

    if login.driver.window_handles[1] == window_after:
        login.driver.switch_to.window(window_after)
        pc.copy(login.driver.current_url)
        groupUrl = pc.paste()
        print(login.driver.title)
        print(groupUrl)

        # Write Url in a file
        # groupUrlForList = str(i) + ". " + groupUrl + "\n"
        groupUrlForList = groupUrl + "\n"

        line_index = 3
        lines = None
        with open('../TextFiles/ProfileFile/15.fb_profile_list_file.txt', 'r') as file_handler:
            lines = file_handler.readlines()

        lines.insert(line_index, groupUrlForList)

        with open('../TextFiles/ProfileFile/15.fb_profile_list_file.txt', 'w') as file_handler:
            file_handler.writelines(lines)

        time.sleep(5)
        login.driver.close()
        login.driver.switch_to.window(window_before)

    else:
        login.driver.switch_to.window(window_before)
        print(" Didn't find Second Tab")


def save_profile_link():
    save_profile_link_actions = ActionChains(login.driver)
    save_profile_link_actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL)
    save_profile_link_actions.perform()


def go_profile_name():
    go_profile_name_actions = ActionChains(login.driver)
    go_profile_name_actions.key_down(Keys.SHIFT).send_keys(Keys.TAB * 1).key_up(Keys.SHIFT)
    go_profile_name_actions.perform()


def close_btn():
    login.driver.implicitly_wait(10)
    close_btn = "//div[@aria-label='Close']"
    close_btn_xpath_aria = login.driver.find_elements_by_xpath(close_btn)
    print(close_btn_xpath_aria)
    print(str(len(close_btn_xpath_aria)) + " Close button found ")

    if login.driver.find_elements_by_xpath(close_btn):
        close_btn_xpath_aria[0].click()


def navigate_hide_btn():
    login.driver.implicitly_wait(10)

    hide_btn = "//div[@aria-label='Hide or report this']"
    hide_btn_xpath_aria = login.driver.find_elements_by_xpath(hide_btn)
    print(hide_btn_xpath_aria)
    print(str(len(hide_btn_xpath_aria)) + " Hide Button found ")

    HideBtnList = []
    for hideBtn in hide_btn_xpath_aria:
        HideBtnList.append(hideBtn)
        print(str(len(HideBtnList) - 1) + " Hide Button")
        hide_btn_xpath_aria[(len(HideBtnList) - 1)].click()
        time.sleep(1)
        hide_btn_xpath_aria[(len(HideBtnList) - 1)].click()
        # print(ReplyBtnXpathAria[(len(ReplyBtnList))])
        try:
            go_profile_name()
            save_profile_link()
            # print(input("Press any Key: "))
            switch_browser_tab()
            time.sleep(2)
        except:
            close_btn()
            pass


login.driver.implicitly_wait(20)
time.sleep(5)

# with open('./groupPostCommentLikeDoneList.txt') as file:
# with open('Campaign\groupPostCommentLikeDoneList.txt') as file:
with open('../TextFiles/GroupFile/groupPostCommentLikeDoneList.txt') as file:
    lines = file.readlines()
    print("We will working with " + str(len(lines)) + " Post")
    index = []
    for groupPost in lines:
        login.driver.get(groupPost)
        # login.driver.get("https://www.facebook.com/groups/366190054572553/permalink/519642729227284/")
        # print(input("Press any Key: "))
        print(login.driver.title)
        print(groupPost + " link")
        time.sleep(2)

        navigate_hide_btn()
        time.sleep(2)
