from Pages.LinkedinPage import LinkedinPage
from Tests.test_base import BaseTest
from Pages.Linkedin_Profile import Linkedin_Profile
from Pages.LinkedingroupPage import Linkedin_Group
from Pages.LinkedinGroupmamber import Linkedin_Group_MEMBER

"""This Test based on that instruction : https://www.youtube.com/watch?v=wkwhGE3Vc5Y"""


class Test_Linkedin(BaseTest):

    def test_check_title(self):
        self.linkedinPage = LinkedinPage(self.driver)
        title = self.linkedinPage.get_title(LinkedinPage.TITLE)
        assert title == LinkedinPage.TITLE

    def test_create_a_post(self):
        self.driver.maximize_window()
        self.linkedinPage = LinkedinPage(self.driver)
        self.linkedinPage.do_post(LinkedinPage.TEST_POST)

    def test_scroll_down(self):
        self.linkedinPage = LinkedinPage(self.driver)
        self.linkedinPage.scroll_down()
        self.linkedinPage.scroll_up()

    def test_get_ele_of_profile_name(self):
        self.linkedinPage = LinkedinPage(self.driver)
        self.linkedinPage.get_element_text(LinkedinPage.PROFILE_NAME)

    def test_get_ele_of_identity(self):
        self.linkedinPage = LinkedinPage(self.driver)
        self.linkedinPage.get_element_text(LinkedinPage.IDENTITY)

    def test_profile(self):
        self.linkedinPage = LinkedinPage(self.driver)
        self.linkedinPage.go_to_profile(LinkedinPage.PROFILE_NAME)

    def test_profile_title(self):
        self.linkedinPage = Linkedin_Profile(self.driver)
        title = self.linkedinPage.get_title(Linkedin_Profile.TITLE)
        assert title == Linkedin_Profile.TITLE

    def test_go_to_group(self):
        self.linkedinPage = LinkedinPage(self.driver)
        self.linkedinPage.do_click(LinkedinPage.GROUP)

    def test_check_group_title(self):
        self.linkedinPage = Linkedin_Group(self.driver)
        title = self.linkedinPage.get_title(Linkedin_Group.GROUP_TITLE)
        assert title == Linkedin_Group.GROUP_TITLE

    def test_see_all_member(self):
        self.driver.maximize_window()
        self.linkedinPage = Linkedin_Group(self.driver)
        self.linkedinPage.do_click(Linkedin_Group.SEE_ALL_MEMBERS)

    def test_member_profile(self):
        self.driver.maximize_window()
        self.linkedinPage = Linkedin_Group_MEMBER(self.driver)
        self.linkedinPage.new_window(Linkedin_Group_MEMBER.SEARCHBAR)









