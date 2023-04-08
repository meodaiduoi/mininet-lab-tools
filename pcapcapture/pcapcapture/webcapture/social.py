from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import (ElementNotInteractableException, ElementClickInterceptedException, 
                                        NoSuchElementException)

from selenium.webdriver.common.keys import Keys

import time
import logging

from webcapture.pageloader import PageLoader


class TiktokLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout=20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(TiktokLoader, self).__init__(
            None,
            timeout, profile_path, preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        # for future implementation
        if 'tiktok.com' in url:
            if 'video' in url:
                super().load(url, (By.ID, 'main-content-video_detail'))
        else:
            logging.error('Not a valid tiktok url')
            
    def next_video(self):
        self._driver.find_element(By.TAG_NAME, 'video').send_keys(Keys.DOWN)

    def previous_video(self):
        self._driver.find_element(By.TAG_NAME, 'video').send_keys(Keys.UP)

    @property
    def captcha_block(self):
        try:
            if self._driver.find_element(By.CLASS_NAME, 'captcha_verify_container'):
                return True
        except NoSuchElementException:
            return False

    # def check_video(self):
    #     try:
    #         self._driver.find_element(
    #             By.CLASS_NAME,
    #             "tiktok-7tjqm6-DivBlurBackground e11s2kul8").get_attribute('style')
    #     except AttributeError:
    #         logging.error('Required to load() first')


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
        if 'facebook.com' in url:
            if 'watch' in url:
                self.page_type = 'watch'
                super().load(url, (By.CSS_SELECTOR, 'svg.x9f619'))
            if 'video' in url:
                self.page_type = 'video'
                super().load(url, (By.CSS_SELECTOR, "i.x14yjl9h > div:nth-child(1) > i:nth-child(1)"))
                self._video_play()
        else:
            logging.error('Not a valid facebook url')

    def _video_play(self):
        try:
            self._driver.find_element(
                (By.CSS_SELECTOR), 
                'i.x14yjl9h > div:nth-child(1) > i:nth-child(1)'
            ).click()
        except AttributeError or ElementNotInteractableException or ElementClickInterceptedException or NoSuchElementException:
            logging.error("Video unplayable")
    
    @property
    def buffer_progress(self):
        '''
        Return the video bufferring progress as a float between 0 and 1
        '''
        try:
            if self.page_type == 'video':
                buffer = self._driver.find_element(By.CSS_SELECTOR, '.x17j41np').get_attribute('style')
                return float(buffer.split(':')[1].split('%')[0]) / 100
            if self.page_type == 'watch':
                buffer =  self._driver.find_element(
                    By.CSS_SELECTOR, 
                    'div.x1d8287x:nth-child(4) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').get_attribute('style')
            return float(buffer.split(':')[1].split('%')[0]) / 100
        except NoSuchElementException:
            logging.error('No video')
        except AttributeError:
            logging.error('Required to load() first')
    
    @property
    def video_progress(self):
        '''
        Returns the current video progress as a float between 0 and 1
        '''
        try:
            if self.page_type == 'video':
                progress = self._driver.find_element(By.CSS_SELECTOR, '.x1evw4sf').get_attribute('style')
            if self.page_type == 'watch':
                progress = self._driver.find_element(
                    By.CSS_SELECTOR, 
                    'div.x1d8287x:nth-child(4) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)').get_attribute('style')
            return float(progress.split(':')[1].split('%')[0]) / 100
        except NoSuchElementException:
            logging.error('No video')
        except AttributeError:
            logging.error('Required to load() first')
    
    def fast_forward(self):
        if self.page_type == 'video':
            self._driver.find_element(By.TAG_NAME, 'video').send_keys(Keys.RIGHT)
        else: 
            logging.error('not implemented for watch pages')
        
    def rewind(self):
        if self.page_type == 'video':
            self._driver.find_element(By.TAG_NAME, 'video').send_keys(Keys.LEFT)
        else: 
            logging.error('not implemented for watch pages')
    
    def play_or_pause(self):
        if self.page_type == 'video':
            self._driver.find_element(By.TAG_NAME, 'video').send_keys(Keys.SPACE)
        else: 
            logging.error('not implemented for watch pages')

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