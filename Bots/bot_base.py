import pathlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
# TODO: We have to solve the userdata problem it have to in one directory
chrome_options.add_argument(f"user-data-dir={scriptDirectory}\\userdata")


class BaseBot:
    def __init__(self):
        self.driver = webdriver.Chrome("../chromedriver.exe", chrome_options=chrome_options)
