from Bots.bot_base import BaseBot
from Config.bot_config import BotData
from Pages.LoginPage import LoginPage


class Bot_Login(BaseBot):
    def test_login_btn_visible(self):
        self.loginPage = LoginPage(self.driver)
        flag = self.loginPage.is_forgotten_password_button_exist()
        assert flag

    def test_login_page_title(self):
        self.loginPage = LoginPage(self.driver)
        title = self.loginPage.get_title(BotData.LOGIN_PAGE_TITLE)
        assert title == BotData.LOGIN_PAGE_TITLE

    def test_login(self):
        self.loginPage = LoginPage(self.driver)
        self.loginPage.do_login(BotData.USER_NAME, BotData.PASSWORD)


# login = Bot_Login()
# fb_page_title = login.test_login()





