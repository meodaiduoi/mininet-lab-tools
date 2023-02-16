from pageloader import PageLoader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os
import random
import time
from logging import warning, info, debug, error

class EcomServiceLoader(PageLoader):

    def __init__(self, url=None, locator=None, delay=20, preferences=None, addons=None):
        super(EcomServiceLoader, self).__init__(locator, delay, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        super().load(url)

    def get_link(self):
        links = []
        all_links = self.driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            if link.get_attribute("href") != None:
                if not link.get_attribute("href").find('https'):
                    links.append(link.get_attribute("href"))
        return links[random.randint(0, len(links)-1)]

    def scroll_to_end(self):
        match = False
        lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        while(match == False):
            lastCount = lenOfPage
            lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            time.sleep(3)
            if lastCount == lenOfPage:
                match = True

class shopee(EcomServiceLoader):

    def __init__(self, url=None, locator=None, delay=20, preferences=None, addons=None):
        super(shopee, self).__init__(url, (By.CLASS_NAME, 'header-with-search__logo-section'), delay, addons)

    def load(self, url):
        super().load(url)

class amazon(EcomServiceLoader):

    def __init__(self, url=None, locator=None, delay=20, preferences=None, addons=None):
        super(amazon, self).__init__(url, (By.ID, 'nav-logo'), delay, addons)

    def load(self, url):
        super().load(url)
