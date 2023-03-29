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
    extensions: A list of paths to the extensions to be added to the firefox profile
    '''

    def __init__(self,
                 url=None,
                 delay=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        super(AmazonLoader,
              self).__init__((By.ID, "nav-xshop"), delay, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'amazon.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid amazon url')


class ShopeeLoader(PageLoader):

    def __init__(self,
                 url=None,
                 delay=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        super(ShopeeLoader,
              self).__init__((By.TAG_NAME, 'footer'), delay, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'shopee.vn' in url:
            super().load(url)
        else:
            logging.error('Not a valid shopee url')


class EbayLoader(PageLoader):

    def __init__(self,
                 url=None,
                 delay=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        super(EbayLoader,
              self).__init__((By.TAG_NAME, "footer"), delay, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'ebay' in url:
            super().load(url)
        else:
            logging.error('Not a valid ebay url')


class TGDDLoader(PageLoader):

    def __init__(self,
                 url=None,
                 delay=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        super(TGDDLoader,
              self).__init__((By.TAG_NAME, "footer"), delay, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'thegioididong.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid thegioididong url')


class TikiLoader(PageLoader):

    def __init__(self,
                 url=None,
                 delay=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        super(TikiLoader,
              self).__init__((By.TAG_NAME, "footer"), delay, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'tiki.vn' in url:
            super().load(url)
        else:
            logging.error('Not a valid tiki url')


# Remove duo to agressive captcha
class LazadaLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        # fix find the footer
        super(LazadaLoader,
              self).__init__((By.TAG_NAME, "div"), timeout, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'lazada.vn' in url:
            super().load(url)
        else:
            logging.error('Not a valid lazada url')


class AlibabaLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout=20,
                 profile_path: str = None,
                 preferences=[],
                 extensions=[],
                 **kwargs):
        # fix find the footer
        super(AlibabaLoader,
              self).__init__((By.TAG_NAME, "div"), timeout, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'alibaba.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid alibaba url')
