import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from Bots.AllPageBot import AllPageBot


all_page = AllPageBot()
file_name = 'BanglaStudent.txt'
try:
    login = all_page.test_login()
    print(input("Press any Key: "))
except:
    print("You already lodged in")

all_page.driver.get("https://www.facebook.com/groups/10ms.programming/posts/2250510671758752/")

# profile_finding_xpath = '//div[@role="article"]//span[@class="nc684nl6"]//span[@dir="auto"]'

all_page.driver.implicitly_wait(10)

# profile_finding_xpath_elements = all_page.driver.find_elements_by_xpath(profile_finding_xpath)

# print(profile_finding_xpath_elements)


def save_file(driver, filename):
    groupUrlForList = driver.current_url + "\n"
    line_index = 3
    lines = None
    with open(filename, 'r') as file_handler:
        lines = file_handler.readlines()
    lines.insert(line_index, groupUrlForList)
    with open(filename, 'w') as file_handler:
        file_handler.writelines(lines)


def switch_tab_save_file(driver, text_file):
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]
    if driver.window_handles[1] == window_after:
        driver.switch_to.window(window_after)
        save_file(driver, text_file)
        time.sleep(2)
        driver.close()
        driver.switch_to.window(window_before)
    else:
        driver.switch_to.window(window_before)
        print(" Didn't find Second Tab")


def mouse_hover(driver, element):
    mouse_hove = ActionChains(driver)
    mouse_hove.move_to_element(element).perform()


def click_and_open_new_tab(driver, element):
    element_action = ActionChains(driver)
    element_action.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()


def collect_profile(driver, profile_lists, text_file):

    profile_index = []
    for profile in profile_lists:
        profile_index.append(profile)
        current_profile = profile_lists[len(profile_index) - 1]

        f = open(text_file, 'r')
        lines = f.readlines()
        if len(profile_index) > len(lines):
            click_and_open_new_tab(driver, current_profile)
            switch_tab_save_file(driver, file_name)
        elif len(profile_index) == len(lines)-1:
            print("We are analyzing")
            mouse_hover(driver, current_profile)
        f.close()


def scroll():
    time.sleep(4)
    scroll_actions = ActionChains(all_page.driver)
    scroll_actions.send_keys(Keys.PAGE_DOWN).perform()


def profile_scrapping(driver, xpath):
    all_profile = all_page.driver.find_elements_by_xpath(xpath)
    driver.implicitly_wait(30)
    print("We are in " + str(len(all_profile)) + " profile")

    collect_profile(all_page.driver, all_profile, file_name)
    scroll()


profile_finding_xpath = '//div[@role="article"]//span[@class="nc684nl6"]//span[@dir="auto"]'


f = open(file_name, 'r')
lines = f.readlines()
print(len(lines))
# for i in range(len(lines)):
for i in range(100):
    print("We are trying " + str(i) + " number time")
    profile_scrapping(all_page.driver, profile_finding_xpath)
f.close()

print("Done Working")

