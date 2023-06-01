from Bots.bot_base import BaseBot
from Pages.MessagePage import MessagePage
from Pages.ProfilePage import ProfilePage


class Bot_MessagePage(BaseBot):
    def test_massage_writing_aria(self):
        self.ProfilePage = ProfilePage(self.driver)
        self.ProfilePage.do_massage_btn_click()

    def test_massage_writing(self, message):
        self.MessagePage = MessagePage(self.driver)
        self.MessagePage.do_massage(message)

    def test_massage_send(self):
        self.MessagePage = MessagePage(self.driver)
        self.MessagePage.do_massage_send_btn_click()

    def test_massage_close(self):
        self.MessagePage = MessagePage(self.driver)
        self.MessagePage.do_massage_close_btn_click()

    def test_hover_new_massage(self):
        self.MessagePage = MessagePage(self.driver)
        self.MessagePage.do_hover_new_massage_btn_click()

    def test_hide_all_massage_close(self):
        self.MessagePage = MessagePage(self.driver)
        self.MessagePage.do_hide_massage_close_btn_click()

    def test_all_massage_close(self):
        self.MessagePage = MessagePage(self.driver)
        self.MessagePage.do_all_massage_close_btn_click()
