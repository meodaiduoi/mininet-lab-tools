from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys

import os
import logging
import time, random
import re
from pytube import Playlist

from webcapture.pageloader import PageLoader
from webcapture.utils import *

class YoutubePlayer(PageLoader):
    '''
    YoutubePlayer class is used to load a youtube video and wait for the video to load completely.
    url: A youtube url to load
    delay: Time to wait for the video to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
   extensions: A list of paths to theextensions to be added to the firefox profile
    '''

    def __init__(self,
                 url: str = None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(YoutubePlayer,
              self).__init__((By.CLASS_NAME, 'html5-main-video'), timeout,
                             profile_path, preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        # check url is from youtube domain
        if 'youtube.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid youtube url')

    @property
    def player_state(self) -> int:
        '''
        Return the state of the player which:
        -1: Unstarted or Advertisement is playing
        0: Ended
        1: Playing
        2: Paused
        3: Unready
        '''
        state_dict = {
            -1: 'Unstarted or Advertisement is playing',
            0: 'Ended',
            1: 'Playing',
            2: 'Paused',
            3: 'Unready'
        }
        try:
            state = self._driver.execute_script(
                "return document.getElementById('movie_player').getPlayerState()"
            )
            logging.info(f'Player state: {state_dict[state]}')
            return state
        except AttributeError:
            logging.error('Required to load() first')

    def play(self):
        if self.player_state == 1:
            logging.error('Player is already playing')
            return
        try:
            self._driver.find_element(By.CLASS_NAME, 'ytp-play-button').click()
            logging.info('Player is playing')
        except AttributeError:
            logging.error('Required to load() first')

    def pause(self):
        if self.player_state == 1:
            try:
                self._driver.find_element(By.CLASS_NAME,
                                          'ytp-play-button').click()
                logging.info('Player is paused')
            except AttributeError:
                logging.error('Required to load() first')
        else:
            logging.error('Player is already not playing')

    def fast_forward(self, times=1):
        '''
        Fast forward the video by pressing the right arrow key on the keyboard
        times: Number of times to press the right arrow key (default: 1) with each time being 5 seconds
        '''
        try:
            self._driver.find_element(By.CLASS_NAME,
                                      'html5-main-video').send_keys(
                                          Keys.RIGHT * times)
        except AttributeError:
            logging.error('Required to load() first')


class YoutubePlaylistFetch(PageLoader):

    def __init__(self,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(YoutubePlaylistFetch,
              self).__init__((By.CLASS_NAME, 'yt-core-image'), timeout,
                             profile_path, preferences, extensions, **kwargs)
        self.url_list = None

    # Don't required webdriver due to access via api
    def get_video_url_playlist(self, playlist_url: str):
        self.url_list = Playlist(playlist_url)
        return self.url_list

    # Will required to open browser for url checking
    def get_live_url_playlist(self, speed=700, delay=1):

        self.start_driver()
        self.load(
            'https://www.youtube.com/playlist?list=PLU12uITxBEPGILPLxvkCc4L_iL7aHf4J2'
        )

        self.scroll_slowly_to_bottom(speed, delay)
        content = self._driver.find_element(By.CSS_SELECTOR, "#contents")
        all_url = content.find_elements(By.CSS_SELECTOR,
                                        ".yt-simple-endpoint#thumbnail")

        url_list = []
        for url in all_url:
            if url.text == 'TRỰC TIẾP' or url.text == 'LIVE':
                url_list.append(url.get_attribute("href"))

        self.close_driver()
        self.url_list = url_list
        return self.url_list


class GMeet(PageLoader):

    def __init__(self,
                 camera_id: int,
                 microphone_id: int,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):

        # !TODO: Change the locator to homepage of meet
        self.preferences = preferences + [
            ('media.navigator.permission.disabled', True),
            ('permissions.default.microphone', camera_id),
            ('permissions.default.camera', microphone_id)
        ]

        self.is_host = None
        super(GMeet, self).__init__(timeout, profile_path, preferences,
                                    extensions, **kwargs)
        self.start_driver()

    def leave_meeting(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='CQylAd']").click()

    def btn_camera(self):
        self._driver.find_element(By.CSS_SELECTOR,
                                  "[jsaction='Az4Fr:Jv50ub']").click()

    def btn_mic(self):
        self._driver.find_element(By.CSS_SELECTOR,
                                  "[jsaction='Az4Fr:Jv50ub']").click()


class GMeetHost(GMeet):
    def __init__(self, camera_id: int, microphone_id: int, timeout: int = 20, profile_path: str = None, preferences: list[tuple[str, str]] = [], extensions: list[str] = [], **kwargs):
        super().__init__(camera_id, microphone_id, timeout, profile_path, preferences, extensions, **kwargs)

    def create_meetting(self) -> str:
        if self.is_host is None or True:
            self.is_host = True
            self.load('https://meet.google.com/',
                      locator=(By.CLASS_NAME, "Y8gQSd BUooTd"))
            self._driver.find_element(
                By.XPATH,
                "/html/body/c-wiz/div/div[2]/div/div[1]/div[3]/div/div[1]/div[1]/div/button/span"
            ).click()
            self._driver.implicitly_wait(2)
            self._driver.find_element(
                By.XPATH,
                "/html/body/c-wiz/div/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/div/ul/li[2]"
            ).click()
            self._driver.implicitly_wait(2)
            for _ in range(5):
                time.sleep(5)
                try:
                    if self._driver.find_element(
                            By.XPATH,
                            '/html/body/div[3]/span/div[2]/div/div/div[2]/div/button'
                    ):
                        self._driver.find_element(
                            By.XPATH,
                            '/html/body/div[3]/span/div[2]/div/div/div[2]/div/button'
                        ).click()
                    logging.info('Meeting created')
                    return self._driver.current_url
                except ElementNotInteractableException or NoSuchElementException:
                    pass
            logging.error('Unable to create meetting')
            return ''

    def accept_guest(self, retry=5) -> bool:
        for _ in range(retry):
            time.sleep(5)
            try:
                if self._driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/button[2]') or :
                    self._driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/button[2]').click()
                    logging.info("Accepted guest")
                    return True
                if self._driver.find_element(By.CSS_SELECTOR, "[class='VfPpkd-BFbNVe-bF1uUb NZp2ef']"):
                    self._driver.find_element(By.CSS_SELECTOR, "[data-mdc-dialog-action='accept']").click()
                    logging.info("Accepted guest")
                    return True
            except ElementNotInteractableException or NoSuchElementException:
                pass
        logging.error("Unable to accept guest")
        return False

        
class GMeetGuest(GMeet):
    def __init__(self, camera_id: int, microphone_id: int, timeout: int = 20, profile_path: str = None, preferences: list[tuple[str, str]] = [], extensions: list[str] = [], **kwargs):
        super().__init__(camera_id, microphone_id, timeout, profile_path, preferences, extensions, **kwargs)
        
    def join_meeting(self, url_invite, retry=5) -> bool:
        # find the element for joining the meeting
        self.is_host = False
        self.load(url_invite, locator=(By.CLASS_NAME, "Y8gQSd BUooTd"))
        for _ in range(retry):
            time.sleep(5)
            try:
                if self._driver.find_element(
                        By.XPATH,
                        "/html/body/div[1]/c-wiz/div/div/div[13]/div[3]/div/div[1]/div[4]/div/div/div[2]/div/div[2]/div[1]/div[1]/button"
                ):
                    self._driver.find_element(
                        By.XPATH,
                        "/html/body/div[1]/c-wiz/div/div/div[13]/div[3]/div/div[1]/div[4]/div/div/div[2]/div/div[2]/div[1]/div[1]/button"
                    ).click()
                    logging.info("Joined the meeting")
                    return True
            except ElementNotInteractableException or NoSuchElementException:
                pass
        logging.error("Unable to join the meeting")
        return False


class GDriveDownloader(PageLoader):
    '''
    GDriveDownloader class is used to download a file from google drive.
    url: A google drive url to download
    download_folder: path to the folder where the file will be downloaded
    timeout: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    '''

    def __init__(self,
                 url: str = None,
                 download_folder: str = './temp',
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        
        # check if it is absolute path or relative path
        mkdir_by_path(mkpath_abs(download_folder))
        
        self.preferences += preferences + [('browser.download.folderList', 2), 
                                           ('browser.download.dir', f'{download_folder}'), 
                                           ('browser.helperApps.neverAsk.saveToDisk',  'application/octet-stream')]
        
        super(GDriveDownloader, self).__init__(
            (By.ID, 'uc-download-link'), timeout, profile_path,
            preferences, extensions, **kwargs)

        self.download_folder = download_folder
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url) -> None:
        if 'drive.google.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid google drive url')

    def download(self) -> None:
        self._driver.find_element(By.ID, 'uc-download-link').click()

    def clean_download(self) -> None:
        # delete all files in download folder
        for file in os.listdir(self.download_folder):
            os.remove(f"{self.download_folder}/{file}")


class GDocsPageLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(GDocsPageLoader,
              self).__init__((By.CLASS_NAME, "jfk-tooltip-contentId"), timeout,
                             profile_path, preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)
        self.strings = []

    def load(self, url):
        if 'docs.google.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid google docs url')

    def editor(self):
        edit = self._driver.find_element(By.TAG_NAME, "canvas")

        for i in range(0, random.randint(550, len(self.strings))):
            ActionChains(self._driver).move_to_element(edit).click(
                edit).send_keys(self.strings[i] + " ").perform()
            time.sleep(random.randrange(0, 1))


class GPhotosPageLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(GPhotosPageLoader,
              self).__init__((By.CLASS_NAME, 'BiCYpc'), timeout, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'photos.google.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid google photos url')


class GmailPageLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(GmailPageLoader,
              self).__init__((By.CLASS_NAME, 'V3 aam'), timeout, profile_path,
                             preferences, extensions, **kwargs)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'mail.google.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid gmail url')
