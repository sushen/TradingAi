import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pathlib
import winsound
import re

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


def driver():
    global driver
    driver = webdriver.Chrome("../chromedriver.exe", chrome_options=chrome_options)
    driver.get("https://facebook.com")


def login():
    try:
        # I use environment veriable  base on this tutorials https://www.youtube.com/watch?v=IolxqkL7cD8
        username = os.environ.get('my_facebook_email')
        password = os.environ.get('my_facebook_pass')

        driver.find_element_by_name("email").send_keys(username)
        driver.find_element_by_name("pass").send_keys(password)
        driver.find_element_by_name("login").click()
        print(input("Press any Key: "))
        print("Login work Successfully ")

    except:
        pass


driver()
login()


def pageStart():
    time.sleep(2)
    driver.implicitly_wait(30)
    pageStartAction = ActionChains(driver)
    pageStartAction.send_keys(Keys.HOME)
    pageStartAction.perform()

def scrollDown():
    time.sleep(2)
    driver.implicitly_wait(30)
    scrollDownAction = ActionChains(driver)
    scrollDownAction.send_keys(Keys.PAGE_DOWN)
    scrollDownAction.perform()

    # print(input("Press any Key: "))

def scrollUp():
    time.sleep(2)
    driver.implicitly_wait(30)
    scrollUpAction = ActionChains(driver)
    scrollUpAction.send_keys(Keys.PAGE_UP)
    scrollUpAction.perform()

def searchWordUsingXpath():
    search_interested_word_xpath = "//div[contains(text(),interested)]"
    searchWordhAria = driver.find_elements_by_xpath(search_interested_word_xpath)
    # print(searchWordhAria)
    # print(str(len(searchWordhAria)) + " interested Word Found")

    if driver.find_elements_by_xpath(search_interested_word_xpath):
        print(str(searchWordhAria[0]) + " :is the Elements" + "\n" + search_interested_word_xpath + " :For this xpath")
        # print(searchWordhAria[0].text)
        allText = searchWordhAria[0].text

        text = allText

        index = []
        for m in re.finditer(r"\binterested\b", text):
            if m.group(0):
                index.append(m)
                print("Present")

                freq = 500
                # duration is set to 100 milliseconds
                dur = 100
                winsound.Beep(freq, dur)
            else:
                print("Absent")
            print(str(len(index)) + " no 'interested' Word Found")

        if len(index) != 0:
            print("Total " + str(len(index)) + " 'interested' Word Found")
            print(input("Press any Key: "))
        else:
            print("No 'interested' Word Found")


def scrollAndSearchUsingXpath():
    for search in range(2):
        time.sleep(5)
        driver.implicitly_wait(30)
        scrollDown()
    for search in range(2):
        time.sleep(5)
        driver.implicitly_wait(30)
        scrollUp()
    grpupPostXpath = "//div[@aria-label='Actions for this post']"
    grpupPostXpathAria = driver.find_elements_by_xpath(grpupPostXpath)
    # print(grpupPostXpathAria)
    print("First " + str(len(grpupPostXpathAria)) + " Post are searching by bot")

    index = []
    for postLoad in grpupPostXpathAria:
        time.sleep(4)
        driver.implicitly_wait(30)
        index.append(postLoad)
        grpupPostXpathAria[len(index)-1].click()
        grpupPostXpathAria[len(index)-1].click()
    pageStart()

def openGropList():
    with open('groupList.txt') as file:
        lines = file.readlines()
        print("We have to work with " + str(len(lines)) + " Groups")

    index = []
    for groupLinkList in lines:
        index.append(groupLinkList)
        print("We are in " + str(len(index)-1) + " no Groups")
        if len(index) > 0:
            driver.get(groupLinkList)
            print(groupLinkList)
            time.sleep(5)
            driver.implicitly_wait(30)
            scrollAndSearchUsingXpath()
            searchWordUsingXpath()
        else:
            print("We are in " + (str(len(index)-1)) + " no Group")
        # print(input("Press any Key: "))

        # Time Counting
        CurrentTime = time.time()
        totalRunningTime = CurrentTime - StartTime
        print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")


openGropList()


# Time Counting
EndTime = time.time()
print("\nThis Script End " + time.ctime())
totalRunningTime = EndTime - StartTime
print("This Script is running for " + str(int(totalRunningTime)) + " Second. or\n")
print("This Script is running for " + str(int(totalRunningTime / 60)) + " Minutes.")