from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from selenium.webdriver.common.keys import Keys

import os
import logging
import time, random
import re
from pytube import Playlist

from webcapture.pageloader import PageLoader


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
                             profile_path, preferences, extensions,
                             **kwargs)
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
                             profile_path, preferences, extensions,
                             **kwargs)
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


class GMeetHost(PageLoader):

    def __init__(self,
                 camera_id: int,
                 microphone_id: int,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, str]] = None,
                 extensions: list[str] = None,
                 **kwargs):
        
        # !TODO: Change the locator to homepage of meet
        self.preferences = preferences + [
            ('media.navigator.permission.disabled', True),
            ('permissions.default.microphone', camera_id),
            ('permissions.default.camera', microphone_id)
        ]
        
        self.is_host = None

        super(GMeetHost,
              self).__init__((By.CLASS_NAME, 'google-material-icons'), timeout,
                             profile_path, preferences, extensions,
                             **kwargs)

        self.start_driver()
    
    def create_meetting(self):
        self.is_host = True
        self.load('https://meet.google.com/')

        pass    
    
    def join_meeting(self, url_invite):
        # find the element for joining the meeting
        self.is_host = False
        self.load(url_invite)

        self._driver.find_element(By.CSS_SELECTOR, "[jsname='Qx7uuf']").click()

    def accept_guest(self):
        # Host Invite
        if self._driver.find_element(By.CSS_SELECTOR,
                                     "[class='VfPpkd-BFbNVe-bF1uUb NZp2ef']"):
            self._driver.find_element(
                By.CSS_SELECTOR, "[data-mdc-dialog-action='accept']").click()
        else:
            print("Continues")

    def leave_meeting(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='CQylAd']").click()

    def btn_camera(self):
        self._driver.find_element(By.CSS_SELECTOR,
                                  "[jsaction='Az4Fr:Jv50ub']").click()

    def btn_mic(self):
        self._driver.find_element(By.CSS_SELECTOR,
                                  "[jsaction='Az4Fr:Jv50ub']").click()


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
        if not os.path.isabs(download_folder):
            download_folder = f'{os.getcwd()}/{download_folder}'
        if not download_folder.endswith('/'):
            download_folder = f'{download_folder}/'

        # check if download folder exists
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        super(GDriveDownloader, self).__init__(
            (By.ID, 'uc-download-link'), timeout, profile_path,
            [('browser.download.folderList', 2),
             ('browser.download.dir', f'{download_folder}'),
             ('browser.helperApps.neverAsk.saveToDisk',
              'application/octet-stream')], extensions,
            **kwargs)

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
                             profile_path, preferences, extensions, 
                             **kwargs)
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

        for i in range(0, random.randint(100, len(self.strings))):
            ActionChains(self._driver).move_to_element(edit).click(
                edit).send_keys(self.strings[i] + " ").perform()
            time.sleep(random.randrange(1, 2))


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
