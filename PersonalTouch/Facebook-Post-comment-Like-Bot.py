import collections
import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pathlib
import pyperclip as pc

# Time Counting
StartTime = time.time()
print("This Script Start " + time.ctime())

# Setting the chrome_options
global chrome_options
chrome_options = Options()
scriptDirectory = pathlib.Path().absolute()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--user-data-dir=chrome-data")
chrome_options.add_argument('--profile-directory=Profile 8')
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument('disable-infobars')
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_argument("user-data-dir=chrome-data")
chrome_options.add_argument(f"user-data-dir={scriptDirectory}\\userdata")

# Setting the driver
global driver
driver = webdriver.Chrome("../chromedriver.exe", chrome_options=chrome_options)
driver.get("https://facebook.com")


def login():
    try:
        # I use environment veriable  base on this tutorials https://www.youtube.com/watch?v=IolxqkL7cD8
        username = os.environ.get('facebook_email')
        password = os.environ.get('facebook_pass')

        driver.find_element_by_id("email").send_keys(username)
        driver.find_element_by_id("pass").send_keys(password)
        driver.find_element_by_name("login").click()
        print(input("Press any Key: "))
        print("Login work Successfully ")

    except:
        pass

login()


def navigateCommentWhenNavigateCommentNotFound():
    driver.implicitly_wait(20)
    time.sleep(2)
    # Navigate Comment Aria
    navigateCommentWhenNavigateCommentNotFoundBtnXpath = "//div[@aria-label='Actions for this post']"
    navigateCommentWhenNavigateCommentNotFoundBtnXpathAria = driver.find_elements_by_xpath(
        navigateCommentWhenNavigateCommentNotFoundBtnXpath)
    if driver.find_elements_by_xpath(navigateCommentWhenNavigateCommentNotFoundBtnXpath):
        navigateCommentWhenNavigateCommentNotFoundBtnXpathAria[0].click()
        navigateCommentWhenNavigateCommentNotFoundBtnXpathAria[0].click()
        print(navigateCommentWhenNavigateCommentNotFoundBtnXpathAria[0])

        navigateCommentWhenNavigateCommentNotFoundActions = ActionChains(driver)
        total_tab = 3
        for i in range(total_tab):
            navigateCommentWhenNavigateCommentNotFoundActions.send_keys(Keys.TAB)
            print(
                str(i + 1) + " tabs Working for navigateCommentWhenNavigateCommentNotFoundActions Like btn navigation")
        navigateCommentWhenNavigateCommentNotFoundActions.send_keys(Keys.ENTER)
        navigateCommentWhenNavigateCommentNotFoundActions.perform()
    else:
        print("Path Not Found ")
        print(input("You Path is not found it will create wrong Navigation fixed it: "))



def navigateLike():
    driver.implicitly_wait(20)
    time.sleep(2)
    # Navigate Profile Massage Aria
    likeBtnXpath = "//span [normalize-space()='Like']"
    # print(likeBtnXpath)
    likeBtnXpathAria = driver.find_elements_by_xpath(likeBtnXpath)
    print(likeBtnXpathAria)

    likeBtnList = []
    try:
        for likeBtn in likeBtnXpathAria:
            likeBtnList.append(likeBtn)
            print(str(len(likeBtnList)) + " Like Btn")
            likeBtnXpathAria[(len(likeBtnList)) * 2].click()
            print(likeBtnXpathAria[(len(likeBtnList)) * 2])
            time.sleep(3)
            # print(input("Press any Key: "))


    except:
        pass

    print("Like Function Working")


def findAndRemoveDuplicate():
    with open('../TextFiles/GroupFile/groupPostDoneLikeList.txt', 'r') as file:
        groupLinks = file.readlines()
        groupLinkSet = set(groupLinks)
        # This loop Expression detect all duplicate item inside list
        duplicateLinks = [item for item, count in collections.Counter(groupLinks).items() if count > 1]
        duplicateLinkSet = set(duplicateLinks)
        uniqueFile = groupLinkSet - duplicateLinkSet
        with open('../TextFiles/GroupFile/groupPostCommentLikeDoneList.txt', 'r') as file:
            sortedGroupLinks = file.readlines()
            sortedGroupLinksSet = set(sortedGroupLinks)
        with open('../TextFiles/GroupFile/groupPostDoneLikeList.txt', 'w') as file:
            # this line delete 2 set String which I store in variable
            sortedUniqueFile = groupLinkSet - sortedGroupLinksSet
            file.writelines(sortedUniqueFile)
        print("We work " + str(len(sortedGroupLinks))
              + " links and \nOur Total group Link is "
              + str(len(sortedGroupLinks)
                    + (len(groupLinks))))


findAndRemoveDuplicate()

driver.implicitly_wait(20)
time.sleep(5)

with open('../TextFiles/GroupFile/groupPostDoneLikeList.txt') as file:
    lines = file.readlines()
    print("We will working with " + str(len(lines)) + " Post")
    index = []
    for groupPost in lines:
        driver.get(groupPost)
        # print(input("Press any Key: "))
        print(driver.title)
        print(groupPost + " link")
        time.sleep(2)

        navigateLike()

        time.sleep(2)
        # print(input("Press any Key: "))

        pc.copy(driver.current_url)
        groupUrl = pc.paste()
        print(driver.title)
        print(groupUrl)

        # Write Url in a file
        # groupUrlForList = str(i) + ". " + groupUrl + "\n"
        groupUrlForList = groupUrl + "\n"

        line_index = 3
        lines = None
        with open('../TextFiles/GroupFile/groupPostCommentLikeDoneList.txt', 'r') as file_handler:
            lines = file_handler.readlines()

        lines.insert(line_index, groupUrlForList)

        with open('../TextFiles/GroupFile/groupPostCommentLikeDoneList.txt', 'w') as file_handler:
            file_handler.writelines(lines)

# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")
