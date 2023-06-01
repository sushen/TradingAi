import random
import time
import os
# import emoji

from wit import Wit
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from Bots.AllPageBot import AllPageBot


all_page = AllPageBot()

try:
    login = all_page.test_login()
    print(input("Press any Key: "))
except:
    print("You already lodged in")

"""We have to go to message page and stay there for some time
 so elements are fully loaded"""

all_page.driver.get("https://www.messenger.com/")
all_page.driver.implicitly_wait(4)


access_token = os.environ.get('wit_access_token')
client = Wit(access_token)


def wit_response(last_message):
    resp = client.message(last_message)
    traits = resp['traits']

    try:
        entity = []
        for key, value in traits.items():
            entity.append(key)
            break
        # print(entity[0][4:])
        return entity[0][4:]
    except:
        pass


def write_and_send(ai_reply):
    try:
        all_page.driver.find_element_by_xpath("//div[@aria-label='Message']").send_keys(ai_reply)
        all_page.driver.find_element_by_xpath('//div[@aria-label="Press Enter to send"]').click()
    except:
        pass


"""We are going to find unread message one by one"""
print(input("Press any Key: "))
# unread_message = all_page.driver.find_elements_by_xpath("//div[@aria-label='Mark as read']/ancestor::div[@data-visualcompletion='ignore-dynamic']")
unread_message = all_page.driver.find_elements_by_xpath("//div[@role='gridcell']/.. //span[@data-visualcompletion='ignore']")
print(len(unread_message))
print(unread_message)

# print(input("Press any Key: "))
for message in unread_message:
    print(input("Press any Key: "))
    message.text
    message.click()
    # print(message.text)
    all_page.driver.implicitly_wait(4)
    time.sleep(4)
    """Every unread message have their last message we have to find it"""
    last_message_text = all_page.driver.find_elements_by_xpath("//div[@class='__fb-light-mode x1n2onr6']")
    latest_message = last_message_text[-1].text
    # facebook have emoji so we need to emoji.demojize the massage to convert emoji to text
    # latest_message = emoji.demojize(latest_message)
    latest_message = latest_message
    print(latest_message)
# """we read the message and take ai help to make the reply"""
    try:
        wit_response(latest_message)
        traits = wit_response(latest_message)

        if traits is None:
            response = input("Make your own Reply: ")
            write_and_send(response)
        elif traits == 'greetings':
            print('hello')
            # TODO: This Should Be a Random Response We can build a partial Ai following this Title : Intelligent AI Chat bot in Python link: Video https://www.youtube.com/watch?v=1lwddP0KUEg
            greeting_list = ['hello', 'hi', 'hy', 'ha']
            response = random.choice(greeting_list)
            write_and_send(response)
    except:
        pass

"""When all the unread reply are done we make the reply base on profile life circle"""

# first_message = all_page.driver.find_element_by_xpath("//span[@dir='auto']/ancestor::div[@data-visualcompletion='ignore-dynamic']/child::a[@aria-current='page']")
# first_message.click()
