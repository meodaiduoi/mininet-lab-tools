from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
                 preferences: list[tuple[str, ...]] = [],
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
                 preferences: list[tuple[str, ...]] = [],
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
                 preferences: list[tuple[str, ...]] = [],
                 extensions: list[str] = [],
                 **kwargs):

        # !TODO: Change the locator to homepage of meet
        preferences.extend([
            ('media.navigator.permission.disabled', True),
            ('permissions.default.microphone', camera_id),
            ('permissions.default.camera', microphone_id)])

        self.is_host = None
        super(GMeet, self).__init__(
            None,
            timeout, profile_path, preferences,
            extensions, **kwargs
            )
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

    def __init__(self,
                 camera_id: int,
                 microphone_id: int,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, ...]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(GMeetHost, self).__init__(camera_id, microphone_id, timeout, profile_path,
                         preferences, extensions, **kwargs)

        self._create_meetting()

    def _create_meetting(self) -> str:
        self.load('https://meet.google.com/',
                  locator=(By.CSS_SELECTOR, ".VfPpkd-LgbsSe-OWXEXe-k8QpJ")) # Create a new meeting button
        try:
            self._driver.find_element(
                By.CSS_SELECTOR,
                ".VfPpkd-LgbsSe-OWXEXe-k8QpJ"
            ).click()
            self._driver.find_element(
                By.CSS_SELECTOR,
                ".JS1Zae" # Start an instant meeting button
            ).click()
        # for _ in range(5):
        #     time.sleep(5)
        #     try:
        #         if self._driver.find_element(
        #                 By.XPATH,
        #                 '/html/body/div[3]/span/div[2]/div/div/div[2]/div/button'
        #         ):
        #             self._driver.find_element(
        #                 By.XPATH,
        #                 '/html/body/div[3]/span/div[2]/div/div/div[2]/div/button'
        #             ).click()
        #         logging.info('Meeting created')
        #         return self._driver.current_url
        #     except ElementNotInteractableException or NoSuchElementException:
        #         pass
        except ElementNotInteractableException or NoSuchElementException:
            logging.error('Unable to create meetting')
            return ''
        return self._driver.current_url

    def accept_guest(self, retry=5) -> bool:
        for _ in range(retry):
            time.sleep(5)
            try:
                if self._driver.find_element(
                        By.XPATH,
                        '/html/body/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/button[2]'
                ):
                    self._driver.find_element(
                        By.XPATH,
                        '/html/body/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/button[2]'
                    ).click()
                    logging.info("Accepted guest")
                    return True
                if self._driver.find_element(
                        By.CSS_SELECTOR,
                        "[class='VfPpkd-BFbNVe-bF1uUb NZp2ef']"):
                    self._driver.find_element(
                        By.CSS_SELECTOR,
                        "[data-mdc-dialog-action='accept']").click()
                    logging.info("Accepted guest")
                    return True
            except ElementNotInteractableException or NoSuchElementException:
                pass
        logging.error("Unable to accept guest")
        return False


class GMeetGuest(GMeet):

    def __init__(self,
                 camera_id: int,
                 microphone_id: int,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, ...]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super().__init__(camera_id, microphone_id, timeout, profile_path,
                         preferences, extensions, **kwargs)

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
                 preferences: list[tuple[str, ...]] = [],
                 extensions: list[str] = [],
                 **kwargs):

        # check if the download folder exists
        if not os.path.exists(download_folder):
            raise FileNotFoundError(f'Folder {download_folder} not found')

        self.download_folder = download_folder

        preferences.extend([
            ('browser.link.open_newwindow', 1),
            ('browser.download.folderList', 2),
            ('browser.download.dir', f'{self.download_folder}'),
            ('browser.download.manager.showWhenStarting', False),
            ('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')])

        super(GDriveDownloader, self).__init__(
            None, timeout, profile_path, preferences,
            extensions, **kwargs)

        self.filesize: tuple[float, str] = None
        self.filename: str = None

        self.start_driver()
        if url:
            self.load(url)

    def load(self, url) -> None:
        if 'drive.google.com' in url:
            super().load(url, (By.CSS_SELECTOR, '.ndfHFb-c4YZDc-Wrql6b-qMHh7d'))

            # if is video file
            if len(download_btn := self._driver.find_elements(
                By.CSS_SELECTOR,
                '.ndfHFb-c4YZDc-bN97Pc-nupQLb-LgbsSe')) > 0:
                download_btn[0].click()

            # if big file
            if len(download_btn := self._driver.find_elements(
                By.CSS_SELECTOR,
                'div.ndfHFb-c4YZDc-C7uZwb-LgbsSe:nth-child(3)')) > 0:
                download_btn[0].click()

            try:
                WebDriverWait(self._driver, self.timeout).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '.uc-name-size')))

                file_info = self._driver.find_element(By.CSS_SELECTOR,
                                                      '.uc-name-size').text
                value, unit = re.compile(r'\((\d+)([A-Z]+)\)').findall(file_info)[0]
                self.filename = re.compile(r'(.*)\s\(').findall(file_info)[0]
                self.filesize = (float(value), unit)

            except TimeoutException or NoSuchElementException:
                logging.error(
                    'Unable to get file info or file is not available')
                return
        else:
            logging.error('Not a valid google drive url')

    @property
    def finished(self, threshold_ratio=0.85, max_download_filesize=-1) -> bool:
        '''
        Check if the download is finished file size is greater than or equal to the file size in the url
        return: True if the download is finished else False
        currently only support for GB and MB filesize
        '''
        if self.filesize:
            filesize_in_dir = os.path.getsize(
                f"{self.download_folder}/{self.filename}")

            unit = {
                'G': 1024 * 1024 * 1024,
                'M': 1024 * 1024,
            }

            filesize_mb = self.filesize[0] * unit[self.filesize[1]]
            if ((filesize_mb > max_download_filesize and max_download_filesize != -1) or
                filesize_in_dir >= filesize_mb * threshold_ratio):
                return True
        return False

    def download(self) -> str:
        try:
            self._driver.find_element(By.ID, 'uc-download-link').click()
        except NoSuchElementException:
            logging.error('Unable to find download button')

    def clean_download(self) -> None:
        # delete all files in download folder
        for file in ls_subfolders(self.download_folder):
            logging.info(f"Deleting {file}")
            os.remove(file)


class GDocsPageLoader(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, ...]] = [],
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

        for i in range(0, random.randint(600, len(self.strings))):
            ActionChains(self._driver).move_to_element(edit).click(
                edit).send_keys(self.strings[i] + " ").perform()
            time.sleep(random.randrange(1, 2))


class GPhoto(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, ...]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(GPhoto,
              self).__init__((By.CLASS_NAME, 'RY3tic'), timeout, profile_path,
                             preferences, extensions, **kwargs)

        self.view_mode = None

        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'photos.google.com' in url:
            super().load(url)
            self.view_mode = 'normal'
        else:
            logging.error('Not a valid google photos url')

    def inspect_image(self) -> bool:
        '''
        Click on the image to inspect
        return: True if image is available else False
        '''
        if len(img_element := self._driver.find_elements(By.CLASS_NAME, 'RY3tic')) > 0:
            img_element[0].click()
            logging.info('Image is available')
            self.view_mode = 'inspect'
            return True
        logging.error('Image is not available')
        return False

    # TODO: REIMPLEMENT THIS
    # def next_inspect_image(self) -> bool:
    #     '''
    #     Requires inspect_image to be called first
    #     Next image in inspect mode
    #     '''
    #     if self.view_mode == 'normal':
    #         logging.error('Not in inspect mode')
    #         return False

    #     next_img_btn = self._driver.find_elements(
    #             By.XPATH,
    #             "//div[contains(@aria-label, 'View next photo')]"
    #         )
    #     if len(next_img_btn) == 0:
    #         logging.error("Can't change image in inspect mode")
    #         return False

    #     for i in range(len(next_img_btn)):
    #         self._driver.execute_script("arguments[0].click()", next_img_btn[i])
    #     return True

class Gmail(PageLoader):

    def __init__(self,
                 url=None,
                 timeout: int = 20,
                 profile_path: str = None,
                 preferences: list[tuple[str, ...]] = [],
                 extensions: list[str] = [],
                 **kwargs):
        super(Gmail,
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

    def send_mail(self, email: str, context: str, message: str):
        try:
            # Click compose button
            self._driver.find_element(By.CSS_SELECTOR,
                                      '.T-I.J-J5-Ji.T-I-KE.L3').click()

            # Enter email address, content, message
            self._driver.find_element(By.NAME, 'to').send_keys(email)
            self._driver.find_element(By.NAME, 'subjectbox').send_keys(context)
            self._driver.find_element(
                By.CSS_SELECTOR, '.Am.Al.editable.LW-avf').send_keys(message)

            # Click send email
            self._driver.find_element(By.CSS_SELECTOR,
                                      '.T-I.J-J5-Ji.aoO.T-I-atl.L3').click()
        except AttributeError:
            logging.error('Required to load() first')
