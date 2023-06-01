from selenium.webdriver.common.by import By

from Config.config import TestData
from Pages.BasePage import BasePage
from Pages.GroupPage import GroupPage


class LoginPage(BasePage):

    """ By Locators - OR """
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "pass")
    NUMBER = (By.ID, "identify_email")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space()='Log In']")
    FORGOTTEN_PASSWORD = (By.LINK_TEXT, "Forgotten password?")
    LOGIN_PAGE_TITLE = "Facebook – log in or sign up"
    LOGIN_PAGE_ENG_LANG_XPATH = (By.XPATH, "//li[normalize-space()='English (UK)']")
    GET_ELE_TEXT = (By.XPATH, "//button[normalize-space()='Log In']")
    CREATE_A_PAGE = (By.LINK_TEXT, "Create a Page")
    CREATE_NEW_ACCOUNT = (By.XPATH, "//a[.='Create New Account']")

    """ constructor of the page class """
    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(TestData.BASE_URL)

    """ Page Action for Login Page """
    """ this is used to get the page title """
    def get_login_page_title(self, title):
        return self.get_title(title)

    """"""
    def is_forgotten_password_button_exist(self):
        return self.is_visible(self.FORGOTTEN_PASSWORD)

    """ this is used to check Forgotten password? Button Link """
    def is_eng_lang_link_exist(self):
        return self.is_visible(self.LOGIN_PAGE_ENG_LANG_XPATH)

    """ this is used to login """
    def do_login(self, username, password):
        self.do_send_keys(self.EMAIL, username)
        self.do_send_keys(self.PASSWORD, password)

    def do_input_click(self, element):
        self.do_click(element)

























