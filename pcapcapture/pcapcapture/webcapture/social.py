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
    def __init__(self, url=None, timeout=20, profile_path: str=None, preferences=None, addons=None):
        super(TiktokLoader, self).__init__((By.CLASS_NAME, "tiktok-xk7ai4-DivHeaderContainer e10win0d0"), timeout, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'tiktok.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid tiktok url')