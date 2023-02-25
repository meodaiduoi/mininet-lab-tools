from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import time
import logging


class PageLoader():
    '''
    PageLoader class is used to load a webpage and wait for the page to load completely.
    locator: A tuple of (By, locator) to wait for the page to load
    delay: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    addons: A list of paths to the addons to be added to the firefox profile
    '''
    def __init__(self, locator=None, timeout: int=3, preferences=None, addons=None):
        self.locator = locator
        self.delay = timeout
        self.preferences = preferences # [(preference_name, preference_value]
        self.extension = addons # [addon_paths]

    def start_driver(self):
        self.firefox_profile = FirefoxProfile()
        if self.preferences:
            for preference in self.preferences:
                self.firefox_profile.set_preference(preference[0], preference[1])

        if self.extension:
            self.firefox_profile.add_extension(self.extension)
        self.driver = webdriver.Firefox()

    def load(self, url):
        try:
            self.driver.get(url)
            if self.locator:
                WebDriverWait(self.driver, self.delay).until(
                    EC.presence_of_element_located(self.locator))
            if not self.locator:
                WebDriverWait(self.driver, self.delay).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'html')))
            logging.info("Page is ready!")
        
        except TimeoutException:
            logging.info("Loading took too much time!")
            self.close_driver()
        except AttributeError as e:
            logging.error('Required to start_driver() first')
        except Exception as e:
            logging.error(e)
            self.close_driver()
            raise e
    
    @property
    def current_height(self):
        return self.driver.execute_script(
            "return document.documentElement.scrollTop || document.body.scrollTop")
    
    @property
    def page_height(self):
        return self.driver.execute_script('return document.body.scrollHeight')

    @property
    def page_source(self):
        return self.driver.page_source

    def scroll_to_specific_height(self, height):
        self.driver.execute_script(f"window.scrollTo(0, {height})")

    def jump_to_top(self):
        self.scroll_to_specific_height(0)

    def jump_to_bottom(self):
        self.scroll_to_specific_height(self.page_height)

    def scroll_slowly_to_bottom(self, speed: int=3, delay: float=1):
        # Scroll slowly to bottom of page
        last_height = self.current_height
        while True:
            self.driver.execute_script(f"window.scrollBy(0, {100 * speed});")
            new_height = self.current_height
            time.sleep(delay)
            if new_height == last_height:
                break
            last_height = new_height

    def close_driver(self, quit=False):
        try:
            if quit:
                self.driver.quit()
            self.driver.close()
        except AttributeError:
            logging.error('Required to load() first')

class SimplePageLoader(PageLoader):
    '''
    SimplePageLoader class is used to load a webpage and wait for the page to load completely.
    '''
    def __init__(self, url=None, timeout=20):
        super().__init__(timeout=timeout)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        super().load(url)