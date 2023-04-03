from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import time
import logging

from webcapture.pageloader import PageLoader


class TiktokLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout=20,
                 profile_path: str = None,
                 preferences=None,
                 extensions=None,
                 **kwargs):
        super(TiktokLoader, self).__init__(
            (By.CLASS_NAME, "tiktok-xk7ai4-DivHeaderContainer e10win0d0"),
            timeout, profile_path, preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'tiktok.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid tiktok url')


class Facebook(PageLoader):
    def __init__(self, url=None, timeout: int = 20, profile_path: str = None, preferences: list[tuple[str, str]] = ..., extensions: list[str] = ..., **kwargs):
        super().__init__((By.CSS_SELECTOR, 'svg.x9f619'), timeout, profile_path, preferences, extensions, **kwargs)
        
        self.start_driver()
        if url:
            self.load(url)
    
    def load(self, url):
        if 'facebook.com/watch/' in url:
            super().load(url)
        else:
            logging.error('Not a valid facebook url')

# class Instagram(PageLoader):
#     pass