"""
This Script sometime run more that 4 hours for collecting data.
It will not collect more that 500 group url.
"""

import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


from Bots.AllPageBot import AllPageBot
from Bots.bot_GropusPage import Bot_GroupPage

file_name = 'GroupName.txt'


# Time Counting
StartTime = time.time()
print("This Script Start " + time.ctime())

all_page = AllPageBot()
group_page = Bot_GroupPage

try:
    login = all_page.test_login()
    print(input("Press any Key after Login: "))
except:
    print("You already lodged in")

profile_finding_xpath = "//a[contains(text(),facebook.com/groups)]/ancestor::div[@data-visualcompletion='ignore-dynamic']"
all_elements = all_page.driver.find_elements_by_xpath(profile_finding_xpath)
print("We found " + str(len(all_elements)) + " Group Elements")

all_page.driver.get("https://www.facebook.com/groups/")

handle = '//div[@data-visualcompletion="ignore" and @data-thumb="1" ]/child::div[@class]'
handle_elements = all_page.driver.find_elements_by_xpath(handle)
print("We found " + str(len(handle_elements)) + " handle")

hover_element_xpath = "//span[contains(text(),'Your Feed')]"
hover_element = all_page.driver.find_element_by_xpath(hover_element_xpath)
print("We found '" + hover_element.text + "' element text")

clickable_elements = handle_elements[0]


def save_file(driver, filename):
    groupUrlForList = driver.current_url + "\n"
    line_index = 3
    lines = None
    with open(filename, 'r') as file_handler:
        lines = file_handler.readlines()
    lines.insert(line_index, groupUrlForList)
    with open(filename, 'w') as file_handler:
        file_handler.writelines(lines)


def click_and_open_new_tab(driver, element):
    element_action = ActionChains(driver)
    driver.implicitly_wait(11)
    time.sleep(2)
    element_action.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()


def switch_tab_save_file(driver, text_file):
    if len(driver.window_handles) == 2:
        window_before = driver.window_handles[0]
        window_after = driver.window_handles[1]

        driver.switch_to.window(window_after)
        save_file(driver, text_file)
        time.sleep(2)
        driver.close()
        driver.switch_to.window(window_before)
    else:
        driver.implicitly_wait(10)
        time.sleep(10)
        print("We are done")


def collect_profile(driver, profile_lists, text_file):
    profile_index = []
    for profile in profile_lists:
        profile_index.append(profile)
        current_profile = profile_lists[len(profile_index) - 1]

        f = open(text_file, 'r')
        lines = f.readlines()
        if len(profile_index) > len(lines):
            click_and_open_new_tab(driver, current_profile)
            switch_tab_save_file(driver, text_file)
        elif len(profile_index) == len(lines)-1:
            print(f"We are start Collecting ' {profile.text} ' We are continuing.... ")

        f.close()


def profile_scrapping(driver, xpath):
    all_profile = driver.find_elements_by_xpath(xpath)
    driver.implicitly_wait(30)
    print("We are in " + str(len(all_profile)) + " Group")
    collect_profile(driver, all_profile, file_name)


def scroll(driver, handle_element):
    driver.implicitly_wait(7)
    time.sleep(4)

    # Time Counting
    ScrollTime = time.time()
    total_running_time = ScrollTime - StartTime
    print("This Scroll is running for " + str(int(total_running_time / 60)) + " Minutes.")

    ActionChains(driver) \
        .drag_and_drop_by_offset(handle_element, 0, 1) \
        .send_keys(Keys.PAGE_DOWN) \
        .send_keys(Keys.PAGE_DOWN) \
        .pause(5) \
        .release(handle_element) \
        .perform()


def small_scroll(driver, handle_element):
    driver.implicitly_wait(7)
    time.sleep(4)

    # Time Counting
    ScrollTime = time.time()
    total_running_time = ScrollTime - StartTime
    print("This Scroll is running for " + str(int(total_running_time / 60)) + " Minutes.")

    ActionChains(driver) \
        .drag_and_drop_by_offset(handle_element, 0, 1) \
        .send_keys(Keys.PAGE_DOWN) \
        .pause(5) \
        .release(handle_element) \
        .perform()


def collect_group(driver, xpath):
    for i in range(40):
        elements = all_page.driver.find_elements_by_xpath(xpath)
        print("We found " + str(i) + " no loop circle " + str(len(elements)) + " Group Elements")
        scroll(driver, clickable_elements)
        profile_scrapping(driver, xpath)


def collect_group_with_small_scroll(driver, xpath):
    for i in range(60):
        elements = all_page.driver.find_elements_by_xpath(xpath)
        print("We found " + str(i) + " no loop circle " + str(len(elements)) + " Group Elements")
        small_scroll(driver, clickable_elements)
        profile_scrapping(driver, xpath)


if (len(all_elements)) <= 500:
    collect_group(all_page.driver, profile_finding_xpath)
    collect_group_with_small_scroll(all_page.driver, profile_finding_xpath)
else:
    print("You nee manual approach to collect extra group contact software owner 'Sushen Biswas'")


print("Done Working")
# Time Counting
EndTime = time.time()
print("This Script End " + time.ctime())
total_Running_time = EndTime - StartTime
print("This Script is running for " + str(int(total_Running_time)) + " Second. or\n")
print("This Script is running for " + str(int(total_Running_time / 60)) + " Minutes.")

