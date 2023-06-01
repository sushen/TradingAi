from selenium.webdriver.common.by import By

from Pages.BasePage import BasePage


class MessagePage(BasePage):
    # MASSAGE_WRITING_ARIA_XPATH = "//div[@class='_1mf _1mj']"
    MASSAGE_WRITING_ARIA_XPATH = "//div[@aria-label='Message']//div[@class='_1mf _1mj']"
    MASSAGE_WRITING_ARIA = (By.XPATH, MASSAGE_WRITING_ARIA_XPATH)
    MASSAGE_SEND_BUTTON = (By.XPATH, "//*[name()='path' and contains(@d,'M16.691502')]")
    MASSAGE_CLOSE_BUTTON = (By.XPATH, "//div[@aria-label='Close chat']//*[local-name()='svg']")
    HOVER_MASSAGE_CLOSE_BUTTON = (By.XPATH, "//div[@class='bp9cbjyn g5ia77u1 j83agx80 j0lfo8lj taijpn5t ocgrx2df irj2b8pg etr7akla']")
    HIDE_MASSAGE_CLOSE_BUTTON = (By.XPATH, "//div[@aria-label='todo']//i[@class='hu5pjgll lzf7d6o1']")
    ALL_MASSAGE_CLOSE_BUTTON = (By.XPATH, "//span[normalize-space()='Close all chats']")

    """ constructor of the page class """
    def __init__(self, driver):
        super().__init__(driver)

    def do_massage(self, massage):
        self.do_send_keys(self.MASSAGE_WRITING_ARIA, massage)

    def do_massage_send_btn_click(self):
        self.do_click(self.MASSAGE_SEND_BUTTON)

    def do_massage_close_btn_click(self):
        self.do_click(self.MASSAGE_CLOSE_BUTTON)

    def do_hover_massage_close_btn(self):
        self.do_click(self.HOVER_MASSAGE_CLOSE_BUTTON)

    def do_hover_new_massage_btn_click(self):
        self.do_hover(self.HOVER_MASSAGE_CLOSE_BUTTON)

    def do_hide_massage_close_btn_click(self):
        self.do_click(self.HIDE_MASSAGE_CLOSE_BUTTON)

    def do_all_massage_close_btn_click(self):
        self.do_click(self.ALL_MASSAGE_CLOSE_BUTTON)
