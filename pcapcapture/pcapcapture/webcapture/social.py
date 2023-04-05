from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import (ElementNotInteractableException, ElementClickInterceptedException, 
                                        NoSuchElementException)

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

    def check_video(self):
        try:
            self._driver.find_element(
                By.CLASS_NAME,
                "tiktok-7tjqm6-DivBlurBackground e11s2kul8").get_attribute('style')
        except AttributeError:
            logging.error('Required to load() first')


class FacebookVideo(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super().__init__(None, timeout,
                         profile_path, preferences, extensions, **kwargs)

        self.page_type = None
        
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if ('facebook.com' and 'watch') in url:
            self.page_type = 'watch'
            super().load(url, (By.CSS_SELECTOR, 'svg.x9f619'))
        if ('facebook.com' and 'video') in url:
            self.page_type = 'video'
            super().load(url, (By.CSS_SELECTOR, "div[data-testid='video_player'"))
            self._video_play()
        else:
            logging.error('Not a valid facebook url')

    def _video_play(self):
        try:
            self._driver.find_element(
                (By.XPATH), 
                '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div/div[2]'
            ).click()
        except AttributeError or ElementNotInteractableException or ElementClickInterceptedException or NoSuchElementException:
            logging.error("Video unplayable")
            
    # def _video_play(self):
    #     try:
    #         if self._driver.find_element(
    #                 By.CSS_SELECTOR,
    #                 "div[data-testid='video_player']").get_attribute(
    #                     "aria-label") == "Play":
    #             self._driver.find_element(
    #                 By.CSS_SELECTOR,
    #                 "div[data-testid='video_player']").click()
        # except AttributeError:
        #     logging.error('Required to load() first')


# class Instagram(PageLoader):
#     pass