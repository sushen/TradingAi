import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
""" This Class is the parents of all page class """
""" This Class contains all the generic method and utilities """

wait_time = 11


class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def do_click(self, by_locator):
        WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(by_locator)).click()

    def do_hover(self, by_locator):
        action = ActionChains(self.driver)
        hover_element = WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(by_locator))
        action.move_to_element(hover_element).perform()

    def do_send_keys(self, by_locator, text):
        WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(by_locator)).send_keys(text)

    def get_element_text(self, by_locator):
        element = WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(by_locator))
        return element.text

    def is_visible(self, by_locator):
        element = WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located(by_locator))
        return bool(element)

    def get_title(self, title):
        WebDriverWait(self.driver, wait_time).until(EC.title_is(title))
        return self.driver.title

    def new_window(self, by_locator):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(by_locator))
        action = ActionChains(self.driver)
        action.send_keys(Keys.TAB).perform()
        new_TAB = ActionChains(self.driver)
        new_TAB.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
        after = self.driver.window_handles[1]
        self.driver.switch_to.window(after)
        time.sleep(5)
        self.driver.close()

    def close_popup(self):
        Action = ActionChains(self.driver)
        Action.key_down(Keys.ESCAPE).key_up(Keys.ESCAPE).perform()

    def scroll_down(self):
        time.sleep(4)
        scroll_actions = ActionChains(self.driver)
        scroll_actions.send_keys(Keys.PAGE_DOWN).perform()

    def scroll_up(self):
        time.sleep(4)
        scroll_actions = ActionChains(self.driver)
        scroll_actions.send_keys(Keys.PAGE_UP).perform()





