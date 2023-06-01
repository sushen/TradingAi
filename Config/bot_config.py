import os


class BotData:
    CHROME_EXECUTABLE_PATH = "../../work_when_sleep/Driver/chromedriver.exe"
    FIREFOX_EXECUTABLE_PATH = "../geckodriver.exe"
    BASE_URL = "https://www.facebook.com/"

    # # Test Account
    # USER_NAME = os.environ.get('facebook_zrliqi_email')
    # PASSWORD = os.environ.get('facebook_zrliqi_pass')

    # My Account
    USER_NAME = os.environ.get('my_facebook_username')
    PASSWORD = os.environ.get('my_facebook_password')

    LOGIN_PAGE_TITLE = "Facebook – log in or sign up"
