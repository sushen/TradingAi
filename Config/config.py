import os


class TestData:
    CHROME_EXECUTABLE_PATH = "../chromedriver.exe"
    FIREFOX_EXECUTABLE_PATH = "../geckodriver.exe"
    BASE_URL = "https://www.facebook.com/"

    USER_NAME = os.environ.get('facebook_zrliqi_email')
    PASSWORD = os.environ.get('facebook_zrliqi_pass')

    LOGIN_PAGE_TITLE = "Facebook – log in or sign up"
