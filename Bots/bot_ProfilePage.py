from Bots.bot_base import BaseBot
from Pages.ProfilePage import ProfilePage


class Bot_ProfilePage(BaseBot):
    def test_massage_button(self):
        self.profilePage = ProfilePage(self.driver)
        self.profilePage.do_massage_btn_click()