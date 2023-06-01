from selenium.webdriver.common.by import By
from Config.Cookies import Cookies
from Config.config import TestData
from Pages.BasePage import BasePage


class Linkedin_Group_MEMBER(BasePage):
    COOKIES_LOCATION = r"./Experiments/Linkedin_Cookies.txt"
    PAGE_URL = "https://www.linkedin.com/groups/25827/members/"
    SEARCHBAR = By.XPATH, "//input[@placeholder='Search members']"
    """ constructor of the page class """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(TestData.LINKEDIN_URL)
        Cookies.load_cookies(self.driver, self.COOKIES_LOCATION)
        self.driver.get(self.PAGE_URL)

    """ Page Action """
    """This is used to check message button"""



