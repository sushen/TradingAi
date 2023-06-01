from selenium.webdriver.common.by import By

from Pages.BasePage import BasePage


class GroupPage(BasePage):
    HEADER = (By.XPATH, "//h1[normalize-space()='Groups']")
    GROUPS_YOU_MANAGE = (By.XPATH, "//span[normalize-space()='Groups you manage']")
    # GROUPS_YOU_JOINED = (By.XPATH, "//span[normalize-space()='Groups you've joined']")
    GROUPS_YOU_JOINED = (By.XPATH, "//span[normalize-space()=" + '"' + "Groups you've joined" + '"' + "]")
    GROUPS_SETTING_ICON = (By.XPATH, "//div[@aria-label='Edit Groups Settings']//i[@class='hu5pjgll op6gxeva']")
    FB_GROUPS_ARIA = (By.XPATH, "//input[@placeholder='Search groups']")

    """ constructor of the page class """
    def __init__(self, driver):
        super().__init__(driver)

    def group_page_title(self, title):
        return self.get_title(title)

    def get_header_value(self):
        if self.is_visible(self.HEADER):
            return self.get_element_text(self.HEADER)

    def get_group_you_manage_value(self):
        if self.is_visible(self.GROUPS_YOU_MANAGE):
            return self.get_element_text(self.GROUPS_YOU_MANAGE)

    def get_group_you_join_value(self):
        if self.is_visible(self.GROUPS_YOU_JOINED):
            return self.get_element_text(self.GROUPS_YOU_JOINED)

    def is_setting_icon_exist(self):
        return self.is_visible(self.GROUPS_SETTING_ICON)


