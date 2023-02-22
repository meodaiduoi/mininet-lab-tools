from pageloader import PageLoader

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import os

from logging import warning, info, debug, error


class AmazonLoader(PageLoader):
    '''
    AmazonLoader class is used to load a amazon service and wait for the page to load completely.
    url: A amazon service url to load
    delay: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    addons: A list of paths to the addons to be added to the firefox profile
    '''
    def __init__(self, url=None, delay=20, preferences=None, addons=None):
        super(AmazonLoader, self).__init__((By.CSS_SELECTOR, "[aria-label='Amazon']"), delay, preferences, addons)
        
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'amazon.com' in url:
            super().load(url)
        else:
            error('Not a valid amazon url')

class ShopeeLoader(PageLoader):
    def __init__(self, url=None, delay=20, preferences=None, addons=None):
        super(ShopeeLoader, self).__init__((By.CLASS_NAME, "Hyfopi"), delay, preferences, addons)
    
    def load(self, url):
        if 'shopee.vn' in url:
            super().load(url)
        else:
            error('Not a valid shopee url')

class TiktokLoader(PageLoader):
    def __init__(self, url=None, delay=20, preferences=None, addons=None):
        super(TiktokLoader, self).__init__((By.CLASS_NAME, "tiktok-xk7ai4-DivHeaderContainer e10win0d0"), delay, preferences, addons)

    def load(self, url):
        if 'tiktok.com' in url:
            super().load(url)
        else:
            error('Not a valid tiktok url')
