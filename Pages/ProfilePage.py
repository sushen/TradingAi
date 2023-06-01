from selenium.webdriver.common.by import By
# from Config.Cookies import Cookies
from Config.config import TestData
from Pages.BasePage import BasePage


class ProfilePage(BasePage):
    COOKIES_LOCATION = "K:\Project\Python\Campaign\Experiments\cookies.txt"
    # COOKIES_LOCATION = "../Experiments/cookies.txt"
    # PROFILE_URL = "https://www.facebook.com/Simpleguyjony"
    PROFILE_URL = "https://www.facebook.com/zrliqi/"
    MASSAGE_BUTTON_XPATH = "//span[contains(text(),'Message')]"
    MASSAGE_BUTTON = (By.XPATH, MASSAGE_BUTTON_XPATH)
    MESSENGER = (By.XPATH, '//div[@aria-label="Message"]')
    STORY_BUTTON = (By.XPATH, "//span[contains(text(),'Add to Story')]")
    PROFILE = (By.XPATH, "//h1[normalize-space()][1]")
    ADD_FRIEND = (By.XPATH, "//div[@class='k4urcfbm']//img[@class='hu5pjgll eb18blue']")
    STATUS = (By.XPATH, "//span[@class='a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7']")
    CREATE_POST = (By.XPATH, "//span[@class='a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7']")
    POST_KEYS = "Hello"
    ABOUT = (By.XPATH, "//span[normalize-space()='About']")
    TEMPORARY_TITLE = "(1) Jony Ghosh | Facebook"
    TITLE = TEMPORARY_TITLE[-10:]
    PHOTO = (By.XPATH, "//span[normalize-space()='Photos']")

    """ constructor of the page class """

    def __init__(self, driver):
        super().__init__(driver)
        # self.driver.get(TestData.BASE_URL)
        # Cookies.load_cookies(self.driver, self.COOKIES_LOCATION)
        # self.driver.get(self.PROFILE_URL)

    """ Page Action """
    """This is used to check message button"""

    def is_message_button_exist(self):
        return self.is_visible(self.MASSAGE_BUTTON)

    def do_massage_btn_click(self):
        self.do_click(self.MASSAGE_BUTTON)

    def is_stroy_btn_exist(self):
        return self.is_visible(self.STORY_BUTTON)

    def do_post(self, post):
        self.do_click(self.CREATE_POST, post)


