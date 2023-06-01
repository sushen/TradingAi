import time
import random
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from Bots.AllPageBot import AllPageBot

all_page = AllPageBot()

try:
    login = all_page.test_login()
    print(input("Press any Key: "))
except:
    print("You already lodged in")

all_page.driver.get("https://www.facebook.com/groups/10ms.programming/posts/2250510671758752/")
print(input("Press any Key: "))

all_page.driver.implicitly_wait(10)


def mouse_hover(driver, element):
    mouse_hove = ActionChains(driver)
    mouse_hove.move_to_element(element).perform()


def scroll():
    time.sleep(4)
    scroll_actions = ActionChains(all_page.driver)
    scroll_actions.send_keys(Keys.PAGE_DOWN).perform()


def single_reply(driver, xpath):
    all_profile = all_page.driver.find_elements_by_xpath(xpath)
    driver.implicitly_wait(30)
    print("We are in " + str(len(all_profile)) + " profile")


reply_xpath = "//div[@role='button'][normalize-space()='Reply']"
reply_selector = all_page.driver.find_elements_by_xpath(reply_xpath)
print(len(reply_selector))

personal_reply = [
    "That's interesting",
    "Wow",
    "whats up"
]

for i in range(len(reply_selector)):
    print("We are trying " + str(i + 1) + " number reply")
    time.sleep(4)
    reply_selector[i].click()
    ActionChains(all_page.driver)\
        .send_keys(random.choice(personal_reply))\
        .pause(2)\
        .send_keys(Keys.ENTER)\
        .perform()


print("Done Working")

