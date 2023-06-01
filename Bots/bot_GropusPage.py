# from Bots.bot_LoginPage import Bot_Login
from Config.config import TestData
# from Pages.GroupPage import GroupPage
from Pages.LoginPage import LoginPage
from Tests.test_base import BaseTest


class Bot_GroupPage(BaseTest):
    def test_group_page_title(self):
        self.login = LoginPage(self.driver)
        group_page = self.login.do_login(TestData.USER_NAME, TestData.PASSWORD)
        title = group_page.group_page_title(TestData.GROUP_PAGE_TITLE)
        assert title == TestData.GROUP_PAGE_TITLE

    def test_group_page_header(self):
        self.login = LoginPage(self.driver)
        group_page = self.login.do_login(TestData.USER_NAME, TestData.PASSWORD)
        header = group_page.get_header_value()
        assert header == TestData.GROUP_PAGE_HEADER

    def test_group_you_manage(self):
        self.login = LoginPage(self.driver)
        group_page = self.login.do_login(TestData.USER_NAME, TestData.PASSWORD)
        header = group_page.get_group_you_join_value()
        assert header == TestData.GROUPS_YOU_MANAGE

    def test_group_you_join(self):
        self.login = LoginPage(self.driver)
        group_page = self.login.do_login(TestData.USER_NAME, TestData.PASSWORD)
        header = group_page.get_group_you_join_value()
        assert header == TestData.GROUPS_YOU_JOINED

    def test_group_setting_icon(self):
        self.login = LoginPage(self.driver)
        group_page = self.login.do_login(TestData.USER_NAME, TestData.PASSWORD)
        assert  group_page.is_setting_icon_exist()







