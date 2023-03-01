from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import os
import logging

from webcapture.pageloader import PageLoader

class AmazonLoader(PageLoader):
    '''
    AmazonLoader class is used to load a amazon service and wait for the page to load completely.
    url: A amazon service url to load
    delay: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    addons: A list of paths to the addons to be added to the firefox profile
    '''
    def __init__(self, url=None, delay=20, profile_path: str=None, preferences=None, addons=None):
        super(AmazonLoader, self).__init__((By.ID, "nav-xshop"), delay, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'amazon.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid amazon url')

class ShopeeLoader(PageLoader):
    def __init__(self, url=None, delay=20, profile_path: str=None, preferences=None, addons=None):
        super(ShopeeLoader, self).__init__((By.CLASS_NAME, "_4FDN71"), delay, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'shopee.vn' in url:
            super().load(url)
        else:
            logging.error('Not a valid shopee url')

class EbayLoader(PageLoader):
    def __init__(self, url=None, delay=20, profile_path: str=None, preferences=None, addons=None):
        super(EbayLoader, self).__init__((By.CLASS_NAME, "gh-ui"), delay, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'ebay.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid ebay url')

class TGDDLoader(PageLoader):
    def __init__(self, url=None, delay=20, profile_path: str=None, preferences=None, addons=None):
        super(TGDDLoader, self).__init__((By.CLASS_NAME, "main-menu"), delay, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'thegioididong.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid thegioididong url')

class TikiLoader(PageLoader):
    def __init__(self, url=None, delay=20, profile_path: str=None, preferences=None, addons=None):
        super(TikiLoader, self).__init__((By.CLASS_NAME, "StyledCategoryList"), delay, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'tiki.vn' in url:
            super().load(url)
        else:
            logging.error('Not a valid tiki url')

class LazadaLoader(PageLoader):
    def __init__(self, url=None, timeout=20, profile_path: str=None, preferences=None, addons=None):
        super(LazadaLoader, self).__init__((By.CLASS_NAME, "lzd-footer"), timeout, profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'lazada.vn' in url:
            super().load(url)
        else:
            logging.error('Not a valid lazada url')

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
