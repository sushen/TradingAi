from selenium.webdriver.common.by import By
from Config.Cookies import Cookies
from Config.config import TestData
from Pages.BasePage import BasePage


class Linkedin_Group(BasePage):
    COOKIES_LOCATION = r"./Experiments/Linkedin_Cookies.txt"
    GROUP_URL = "https://www.linkedin.com/groups/13740423/"
    GROUP_TITLE = "Python Developers Community (moderated) | Groups | LinkedIn"
    SEE_ALL_MEMBERS = By.XPATH, "//a[@href='/groups/25827/members/']"
    """ constructor of the page class """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(TestData.LINKEDIN_URL)
        Cookies.load_cookies(self.driver, self.COOKIES_LOCATION)
        self.driver.get(self.GROUP_URL)

    """ Page Action """
    """This is used to check message button"""



