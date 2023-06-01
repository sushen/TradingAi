from selenium.webdriver.common.by import By
from Config.Cookies import Cookies
from Config.config import TestData
from Pages.BasePage import BasePage


class Linkedin_Profile(BasePage):
    COOKIES_LOCATION = r"./Experiments/Linkedin_Cookies.txt"
    PROFILE_URL = "https://www.linkedin.com/in/jony-ghosh-9baa5721a/"
    TITLE = "Jony Ghosh | LinkedIn"
    """ constructor of the page class """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(TestData.LINKEDIN_URL)
        Cookies.load_cookies(self.driver, self.COOKIES_LOCATION)
        self.driver.get(self.PROFILE_URL)

    """ Page Action """
    """This is used to check message button"""

    def go_to_profile(self, element):
        self.do_click(element)


