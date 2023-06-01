import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from Config.config import TestData

""" Three thing we have to do extra"""

# 1 Work with chrome option
import pathlib
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
chrome_options.add_argument(f"user-data-dir={scriptDirectory}\\userdata")


# 2 We have to use 1 params
@pytest.fixture(params=["chrome"], scope="class")
def init_driver(request):
    if request.param == "chrome":
        web_driver = webdriver.Chrome(executable_path=TestData.CHROME_EXECUTABLE_PATH)
        # web_driver = webdriver.Chrome(ChromeDriverManager().install())
    if request.param == "firefox":
        web_driver = webdriver.Chrome(executable_path=TestData.FIREFOX_EXECUTABLE_PATH)
    request.cls.driver = web_driver
    # 3 We cannot close browser so we comment it
    yield
    web_driver.close()







