import time

from selenium.webdriver.common.by import By
from Config.Cookies import Cookies
from Config.config import TestData
from Pages.BasePage import BasePage


class LinkedinPage(BasePage):
    COOKIES_LOCATION = r"./Experiments/Linkedin_Cookies.txt"
    FEED_URL = "https://www.linkedin.com/feed/"
    TITLE = "Feed | LinkedIn"
    PROFILE_NAME = (By.XPATH, "//div[@class='profile-rail-card__actor-link t-16 t-black t-bold']")
    IDENTITY = (By.XPATH, "//p[@class='identity-headline t-12 t-black--light t-normal mt1']")
    MESSAGE_BUTTON = (By.XPATH, "//a[@data-control-name='nav_messaging' and @id='ember25']")
    GROUP = (By.XPATH, "//a[@href='https://www.linkedin.com/groups/25827']")
    POST = (By.XPATH, "//span[normalize-space()='Start a post']")
    JOIN_NOW = By.XPATH, "//a[normalize-space()='Join now']"
    MY_NETWORK = (By.XPATH, "//a[@data-test-global-nav-link='mynetwork']")
    MEMBER_PROFILE = (By.XPATH, "//a[@id='ember1122']")
    POST_FIELD = (By.XPATH, "//div[@aria-placeholder='What do you want to talk about?']")
    SAVE_POST = (By.XPATH, "//button[@aria-label='Save this post']")
    TEST_POST = "Linkedin post"
    CLOSE_POST = (By.XPATH, "//button[@id='ember158']//li-icon[@type='cancel-icon']//*[local-name()='svg']")
    DISCARD = (By.XPATH, "//span[normalize-space()='Discard']")
    """ constructor of the page class """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(TestData.LINKEDIN_URL)
        Cookies.load_cookies(self.driver, self.COOKIES_LOCATION)
        self.driver.get(self.FEED_URL)

    """ Page Action """
    """This is used to check message button"""

    def go_to_profile(self, element):
        self.do_click(element)

    def open_new_window(self, element):
        # before = self.driver.window_handles[0]
        # self.driver.switch_to.window(before)
        self.new_window(element)

    # def get_profile_title(self, title):
    #     Title = self.get_title(title)
    #     return Title[-10:]

    def do_post(self, post):
        self.do_click(self.POST)
        time.sleep(2)
        self.do_send_keys(self.POST_FIELD, post)
        time.sleep(2)
        self.close_popup()
        self.do_click(self.DISCARD)

