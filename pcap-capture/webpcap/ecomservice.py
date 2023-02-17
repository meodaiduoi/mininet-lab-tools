from pageloader import PageLoader

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import os

from logging import warning, info, debug, error

class EcomServiceLoader(PageLoader):
    '''
    EcomServiceLoader class is used to load a ecom service and wait for the page to load completely.
    url: A ecom service url to load
    delay: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    addons: A list of paths to the addons to be added to the firefox profile
    '''
    def __init__(self, url=None, delay=20, preferences=None, addons=None):
        pass

    def load(self, url):
        pass

class AmazonLoader(EcomServiceLoader):
    '''
    AmazonLoader class is used to load a amazon service and wait for the page to load completely.
    url: A amazon service url to load
    delay: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    addons: A list of paths to the addons to be added to the firefox profile
    '''
    def __init__(self, url=None, delay=20, preferences=None, addons=None):
        super().__init__(url, delay, preferences, addons)

    def load(self, url):
        pass
