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

    @property
    def meet_url(self):
        return self._driver.current_url
    
    @property
    def meet_code(self):
        match = re.search(r"/([a-z0-9-]+)\?", self.meet_url)
        if match:
            meeting_id = match.group(1)
            return meeting_id
    
    def leave_meeting(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='CQylAd']").click()

    def btn_camera(self):
        try:
            if self._driver.find_element(By.XPATH, 
                                        '//div[@role="button"][@aria-label="Tắt máy ảnh (Ctrl + E)"]'):
                logging.info('Camera is on')
            else:
                self._driver.find_element(By.XPATH,
                                    '//div[@role="button"][@aria-label="Bật máy ảnh (Ctrl + E)"]').click()
                logging.info('Turn on camera')
        except AttributeError:
            logging.error('No find camera button element')
            
    def btn_mic(self):
        try:
            if self._driver.find_element(By.XPATH, 
                                        '//div[@role="button"][@aria-label="Tắt micrô (Ctrl + D)"]'):
                logging.info('Mic is on')
            else:
                self._driver.find_element(By.XPATH,
                                    '//div[@role="button"][@aria-label="Bật micrô (Ctrl + D)"]').click()
                logging.info('Turn on mic')
        except AttributeError:
            logging.error('No find mic button element')

    @property
    def mic_status(self) -> int:
        state_dict = { 0: 'off', 1: 'on' }

        try:
            status = self._driver.find_element(By.CSS_SELECTOR, '.VfPpkd-P5QLlc')
            if bool(status.get_attribute('data-is-muted')):
                logging.info(f'Mic device {state_dict[0]}')
                return 0
            logging.info(f'Mic device {state_dict[1]}')
            return 1
        except NoSuchElementException:
            logging.error('Unable to find mic element')
            return -1
            
    @property
    def cam_status(self) -> int:
        state_dict = {  -1: 'error', 0: 'off', 1: 'on' }
        try:
            status = self._driver.find_element(By.CSS_SELECTOR, ".eaeqqf")
            if bool(status.get_attribute('data-is-muted')):
                if status.get_attribute('aria-label') == 'Sự cố với máy ảnh. Hiện thêm thông tin':
                    logging.error(f'Camera device {state_dict[-1]}')
                    return -1
                logging.info(f'Camera device {state_dict[0]}')
                return 0
            logging.info(f'Camera device {state_dict[1]}')
            return 1
        except NoSuchElementException:
            logging.error('Unable to find camera element')    
            return -1
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

    
    # !TODO: refactor this function when have time for now it's working don't touch it
    def create_meeting(self) -> str:
        self.load('https://meet.google.com/',
                locator=(By.CSS_SELECTOR, ".VfPpkd-LgbsSe-OWXEXe-k8QpJ"))  # Create a new meeting button

        try:
            self._driver.find_element(By.CSS_SELECTOR, ".VfPpkd-LgbsSe-OWXEXe-k8QpJ").click()
            self._driver.find_element(By.CSS_SELECTOR, ".JS1Zae").click()  # Start an instant meeting button
            WebDriverWait(self._driver, self.timeout).until(EC.visibility_of_element_located(((By.XPATH, "//Button[contains(., 'OK')]"))))
            self._driver.find_element(By.XPATH, "//Button[contains(., 'OK')]").click() # Safety notfications close button
        except (ElementNotInteractableException, NoSuchElementException, TimeoutException):
            logging.error('Unable to create meeting')
            return ''
        return self._driver.current_url


    def accept_guest(self) -> bool:
        try:
            self._driver.find_element(By.XPATH, "//Button[contains(., 'Chấp nhận')]").click()
            logging.info("Accepted guest")
            return True
        except (ElementNotInteractableException, NoSuchElementException):
            logging.error("Unable to accept guest or no guest")
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

        
    def load(self, url_invite) -> bool:
        # find the element for joining the meeting
        self.is_host = False
        super().load(url_invite, (By.CLASS_NAME, 'mFzCLe'))
        self._join_meeting()
    
    def _join_meeting(self):
        try:
            WebDriverWait(self._driver, self.timeout).until(
                EC.visibility_of_element_located((
                    By.XPATH, "//Button[contains(., 'Yêu cầu tham gia') or contains(., 'Tham gia ngay')]")))
        except TimeoutException:
            logging.error('Unable to join meeting, page not loaded')
            return False

        join_buttons = self._driver.find_elements(By.XPATH, "//Button[contains(., 'Yêu cầu tham gia') or contains(., 'Tham gia ngay')]")
        if not join_buttons:
            logging.error(f'Unable to find join button on meeting url: {self.meet_url}')
            return False

        for button in join_buttons:
            try:
                button.click()
            except ElementNotInteractableException:
                pass

        logging.info(f'Joined meeting url: {self.meet_url}')
        return True

    @property        
    def joined(self) -> bool:
        if len(self._driver.find_elements(
                By.CSS_SELECTOR,
                ".pKgFkf")) > 0:
            logging.info(f'You joined the meeting room')
            return True
        elif len(self._driver.find_elements(
            By.CSS_SELECTOR, 
            ".oZ3U3b")) > 0:   
            logging.info(f'You are in the waiting room')
            return False
        else:
            logging.error(f'Unable to join meeting url')
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

    def _arrow_click(self, arrow):
        try:
            if arrow == 'DOWN':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.DOWN)
                logging.info('Send key DOWN to body')

            if arrow == 'UP':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.UP)
                logging.info('Send key UP to body')

            if arrow == 'LEFT':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.LEFT)
                logging.info('Send key Left to body')

            if arrow == 'RIGHT':
                self._driver.find_element(By.CSS_SELECTOR,
                                          "body").send_keys(Keys.RIGHT)
                logging.info('Send key Right to body')

        except AttributeError:
            logging.error('Required to load() first')

    def next_inspect_image(self) -> bool:
        '''
        Requires inspect_image to be called first
        Next image in inspect mode
        '''
        if self.view_mode == 'normal':
            logging.error('Not in inspect mode')
            return False

        # next_img_btn = self._driver.find_elements(
        #         By.XPATH,
        #         "//div[contains(@aria-label, 'View next photo')]"
        #     )
        # if len(next_img_btn) == 0:
        #     logging.error("Can't change image in inspect mode")
        #     return False

        # for i in range(len(next_img_btn)):
        #     self._driver.execute_script("arguments[0].click()", next_img_btn[i])
        
        logging.info('Changing next image in inspect mode')
        self._arrow_click('RIGHT')
        return True


    def scroll_slowly_to_bottom(self, scroll_time: int = 3, delay: float = 1):
        '''
        Scroll slowly to bottom of page
        '''
        for _ in range(scroll_time):
            logging.info('Scrolling slowly to bottom')
            self._driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(delay)

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
