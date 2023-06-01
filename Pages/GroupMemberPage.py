from Config.Cookies import Cookies
from Config.config import TestData
from Pages.BasePage import BasePage


class GroupMemberPage(BasePage):
    COOKIES_LOCATION = "K:\Project\Python\Campaign\Experiments\cookies.txt"
    # COOKIES_LOCATION = "../Experiments/cookies.txt"
    GROUP_PAGE_MEMBER_URL = "https://www.facebook.com/groups/366190054572553/members/things_in_common"
    GROUP_PAGE_INPUT_XPATH = "//input[@placeholder='Find a member']"

    """ constructor of the page class """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(TestData.BASE_URL)
        Cookies.load_cookies(self.driver, self.COOKIES_LOCATION)
        self.driver.get(self.GROUP_PAGE_MEMBER_URL)

    """ Page Action """
    """This is used to send Text"""
    def is_input_aria_click(self):
        self.do_click(self.GROUP_PAGE_INPUT_XPATH)


