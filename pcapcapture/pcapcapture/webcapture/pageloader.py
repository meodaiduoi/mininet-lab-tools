from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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

    def __init__(self, locator=None, timeout: int=20,
                 profile_path: str=None, 
                 preferences: list[tuple[str, str]]=[], 
                 extensions: list[str]=[],
                 **kwargs):
        self.locator = locator
        self.delay = timeout
        self.profile_path = profile_path
        self.preferences = preferences # [(preference_name, preference_value),../]
        self.extensions = extensions # [addon_paths]
        self._driver = None
        if kwargs.get('disable_cache', False):
            self.preferences += [('browser.cache.disk.enable', False),
                                 ('browser.cache.memory.enable', False),
                                 ('browser.cache.offline.enable', False),
                                 ('network.cookie.cookieBehavior', 5)]

        if kwargs.get('disable_http3', False):
            self.preferences += [('network.http.http3.enable', False)]

    def start_driver(self):
        self.firefox_profile = FirefoxProfile()
        if self.profile_path:
            self.firefox_profile = FirefoxProfile(self.profile_path)
        for preference in self.preferences:
            self.firefox_profile.set_preference(preference[0], preference[1])
        for extension in self.extensions:
            self.firefox_profile.add_extension(extension)
        self._driver = webdriver.Firefox(self.firefox_profile)

    def load(self, url, locator=None):
        if locator:
            self.locator = locator
        try:
            self._driver.get(url)
            if self.locator:
                WebDriverWait(self._driver, self.delay).until(
                    EC.presence_of_element_located(self.locator))
            if not self.locator:
                WebDriverWait(self._driver, self.delay).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'html')))
            logging.info("Page is ready!")

        except TimeoutException:
            logging.error("Loading took too much time!")
            self.close_driver()
        except AttributeError as e:
            logging.error('Required to start_driver() first')
        except Exception as e:
            self.close_driver()
            logging.critical(f'fatal error: {e}')
            raise e

    @property
    def current_height(self):
        return self._driver.execute_script(
            "return document.documentElement.scrollTop || document.body.scrollTop"
        )

    @property
    def page_height(self):
        return self._driver.execute_script('return document.body.scrollHeight')

    @property
    def page_source(self):
        return self._driver.page_source
    
    @property
    def page_url(self):
        return self._driver.current_url

    def scroll_to_specific_height(self, height):
        self._driver.execute_script(f"window.scrollTo(0, {height})")

    def jump_to_top(self):
        self.scroll_to_specific_height(0)

    def jump_to_bottom(self):
        self.scroll_to_specific_height(self.page_height)

    def scroll_slowly_to_bottom(self, speed: int = 3, delay: float = 1):
        # Scroll slowly to bottom of page
        last_height = self.current_height
        while True:
            self._driver.execute_script(f"window.scrollBy(0, {speed});")
            new_height = self.current_height
            time.sleep(delay)
            if new_height == last_height:
                break
            last_height = new_height

    def arrow_click(self, arrow):
        try:
            if arrow == 'DOWN':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.DOWN)
            else:
                logging.error('Check to word')
            if arrow == 'UP':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.UP)
            else:
                logging.error('Check to word')
            if arrow == 'LEFT':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.LEFT)
            else:
                logging.error('Check to word')
            if arrow == 'RIGHT':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.RIGHT)
            else:
                logging.error('Check to word')
        except AttributeError:
            logging.error('Required to load() first')
            
    def clean_history(self):
        self._driver.delete_all_cookies()
        self._driver.execute_script("window.localStorage.clear();")
        self._driver.execute_script("window.sessionStorage.clear();")
        self._driver.execute_script("window.indexedDB.deleteDatabase('cookies');")
        self._driver.execute_script("window.indexedDB.deleteDatabase('localstorage');")
        self._driver.execute_script("window.indexedDB.deleteDatabase('sessionstorage');")

    def close_driver(self, quit=False):
        try:
            if quit:
                self._driver.quit()
            self._driver.close()
            self._driver = None
        except AttributeError:
            logging.error('Required to load() first')


class SimplePageLoader(PageLoader):
    '''
    SimplePageLoader class is used to load a webpage.
    '''

    def __init__(self,
                 url=None,
                 timeout=20,
                 profile_path=None,
                 preferences=[],
                 extensions=[],
                **kwargs):
        super().__init__(timeout=timeout,
                         profile_path=profile_path,
                         preferences=preferences,
                         extensions=extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    @property
    def driver(self):
        return self._driver