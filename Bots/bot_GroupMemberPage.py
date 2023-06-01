from Bots.bot_base import BaseBot
# from Pages.GroupMemberPage import GroupMemberPage


class Bot_GroupMemberPage(BaseBot):
    def test_search_input_aria(self):
        self.groupMemberPage = GroupMemberPage(self.driver)
        self.groupMemberPage.is_input_aria_click()