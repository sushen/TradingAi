from Config.config import TestData
from Pages.ProfilePage import ProfilePage
from Tests.test_base import BaseTest


class Test_ProfilePage(BaseTest):

    def test_profile_page_title(self):
        self.profilePage = ProfilePage(self.driver)
        title1 = self.profilePage.get_title(TestData.PROFILE_PAGE_TITLE)
        assert title1 == TestData.PROFILE_PAGE_TITLE
