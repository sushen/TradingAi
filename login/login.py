import os
from selenium.webdriver.common.by import By

from driver.driver import Driver


class Login:
    def login(self, driver):
        # print(input("Inside class and function :"))
        try:
            # I use environment variable  base on this tutorials https://www.youtube.com/watch?v=IolxqkL7cD8
            username = os.environ.get('facebook_email')
            password = os.environ.get('facebook_pass')
            driver.find_element(By.NAME, "email").send_keys(username)
            driver.find_element(By.NAME, "pass").send_keys(password)
            driver.find_element(By.NAME, "login").click()

            print(input("Login work Successfully Press any Key: "))
        except:
            pass




# driver = Driver().driver

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# driver = webdriver.Chrome("../chromedriver.exe", chrome_options=chrome_options)
# driver.get("https://www.facebook.com/")
# Login().login(driver)
