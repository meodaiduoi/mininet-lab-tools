
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

from webcapture.pageloader import PageLoader

class YoutubePlayer(PageLoader):
    '''
    YoutubePlayer class is used to load a youtube video and wait for the video to load completely.
    url: A youtube url to load
    delay: Time to wait for the video to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    addons: A list of paths to the addons to be added to the firefox profile
    '''
    def __init__(self, url: str=None, timeout: int=20, profile_path: str=None,
                 preferences: list[tuple[str, str]]=None, addons: list[str]=None):
        super(YoutubePlayer, self).__init__((By.CLASS_NAME, 'html5-main-video'),
                                            timeout, profile_path,
                                            preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        # check url is from youtube domain
        if 'youtube.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid youtube url')

    def get_player_state(self) -> int:
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
                "return document.getElementById('movie_player').getPlayerState()")
            logging.info(f'Player state: {state_dict[state]}')
            return state
        except AttributeError:
            logging.error('Required to load() first')

    def play(self):
        player_sate = self.get_player_state()
        if player_sate == 1:
            logging.error('Player is already playing')
            return
        try:
            self._driver.find_element(By.CLASS_NAME,'ytp-play-button').click()
            logging.info('Player is playing')
        except AttributeError as e:
            logging.error('Required to load() first')

    def pause(self):
        player_sate = self.get_player_state()
        if player_sate == 1:
            try:
                self._driver.find_element(By.CLASS_NAME,'ytp-play-button').click()
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
            self._driver.find_element(
                By.CLASS_NAME,'html5-main-video').send_keys(Keys.RIGHT * times)
        except AttributeError:
            logging.error('Required to load() first')

class YoutubeLivePlayer(PageLoader):
    def __init__(self, timeout: int=20, profile_path: str=None,
                 preferences: list[tuple[str, str]]=None,  addons: list[str]=None):
        self.timeout = timeout
        self.preferences = preferences
        self.addons = addons
        super(YoutubeLivePlayer, self).__init__((By.CLASS_NAME, 'yt-core-image'),
                                            timeout, profile_path,
                                            preferences, addons)
        self.start_driver()
        self.load(
            'https://www.youtube.com/playlist?list=PLU12uITxBEPGILPLxvkCc4L_iL7aHf4J2'
        )
        self.url_list = self.__get_stream_url_list()
        self.yliveplayer = None

    def __get_stream_url_list(self, speed=700, delay=1):
        self.scroll_slowly_to_bottom(speed, delay)
        content = self._driver.find_element(By.CSS_SELECTOR,"#contents")
        all_url = content.find_elements(
            By.CSS_SELECTOR,".yt-simple-endpoint#thumbnail")

        url_list = []
        for url in all_url:
            if url.text == 'TRỰC TIẾP' or url.text == 'LIVE':
                url_list.append(url.get_attribute("href"))
        self.close_driver()
        return url_list

    def load_in_playlist(self, id: -1=int)-> str:
        if self.yliveplayer:
            self.close()
        if id not in range(len(self.url_list)):
            id = random.randint(0, len(self.url_list))

        self.yliveplayer = YoutubePlayer(
            self.url_list[id],
            self.timeout,
            self.preferences,
            self.addons
        )
        return self.url_list[id]

    def play(self):
        self.yliveplayer.play()

    def pause(self):
        self.yliveplayer.pause()

    def get_player_state(self):
        return self.yliveplayer.get_player_state()

    def close(self, quit=False):
        self.yliveplayer.close_driver(quit)
        self.yliveplayer = None
class GMeetHost(PageLoader):
    def __init__(self, url=None, timeout: int=20, profile_path: str=None,
                 preferences: list[tuple[str, str]]=None, addons: list[str]=None):
        # !TODO: Change the locator to homepage of meet
        super(GMeetHost, self).__init__((By.CLASS_NAME, 'google-material-icons'),
                                        timeout, profile_path,
                                        preferences, addons)

        self.start_driver()
        if url:
            self.load(url)

    def user(self, name, passwrd):
        self.name = name
        self.passwrd = passwrd

    def signin(self):
        try:
            # Click button sign-in
            self._driver.find_element(By.CLASS_NAME, "glue-header__link ").click()

            # Input user account
            username = self._driver.find_element(By.ID, 'identifierId')
            username.send_keys(self.name)
            nextButton = self._driver.find_element(By.ID, 'identifierNext')
            nextButton.click()

            # Input user password
            password = self._driver.find_element(By.CSS_SELECTOR, "[aria-label='Enter your password']")
            password.send_keys(Keys.BACK_SPACE*20, self.passwrd)
            signInButton = self._driver.find_element(By.ID,'passwordNext')
            signInButton.click()
        except AttributeError as e:
            logging.error('Required to user() first')

    def code_meet(self, code):
        # Create code meet before
        self.code = code

    def input_code(self):
        try:
            # find the element for entering meeting code
            code_input = self._driver.find_element(By.ID, "i6")

            # enter the meeting code
            code_input.send_keys(self.code)

            # press enter key
            code_input.send_keys(Keys.RETURN)
        except AttributeError as e:
            logging.error('Required to code_meet() first')

    def join_meeting(self):
        # find the element for joining the meeting
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='Qx7uuf']").click()

    def accept_guest(self):
        # Host Invite
        if self._driver.find_element(By.CSS_SELECTOR, "[class='VfPpkd-BFbNVe-bF1uUb NZp2ef']"):
            self._driver.find_element(By.CSS_SELECTOR, "[data-mdc-dialog-action='accept']").click()
        else:
            print("Continues")

    def leave_meeting(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='CQylAd']").click()

    def btn_camera(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsaction='Az4Fr:Jv50ub']").click()

    def btn_mic(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsaction='Az4Fr:Jv50ub']").click()

class GMeetGuest(PageLoader):
    def __init__(self, url=None, timeout: int=20, profile_path: str=None,
                 preferences: list[tuple[str, str]]=None, addons: list[str]=None):
        super(GMeetGuest, self).__init__((By.CLASS_NAME, 'google-material-icons'), timeout,
                                         profile_path, preferences, addons)

        self.start_driver()
        if url:
            self.load(url)

    def user(self, name, passwrd):
        self.name = name
        self.passwrd = passwrd

    def signin(self):
        try:
            # Click button sign-in
            self._driver.find_element(By.CLASS_NAME, "glue-header__link ").click()

            # Input user account
            username = self._driver.find_element(By.ID, 'identifierId')
            username.send_keys(self.name)
            nextButton = self._driver.find_element(By.ID, 'identifierNext')
            nextButton.click()

            # Input user password
            password = self._driver.find_element(By.CSS_SELECTOR, "[aria-label='Enter your password']")
            password.send_keys(Keys.BACK_SPACE*20, self.passwrd)
            signInButton = self._driver.find_element(By.ID,'passwordNext')
            signInButton.click()
        except AttributeError:
            logging.error('Required to user() first')

    def code_meet(self, code):
        # Code GHost
        self.code = code

    def input_code(self):
        try:
            # find the element for entering meeting code
            code_input = self._driver.find_element(By.ID, "i6")

            # enter the meeting code
            code_input.send_keys(self.code)

            # press enter key
            code_input.send_keys(Keys.RETURN)
        except AttributeError:
            logging.error('Required to code_meet() first')

    def join_meeting(self):
        # find the element for joining the meeting
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='Qx7uuf']").click()

    def leave_meeting(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsname='CQylAd']").click()

    def btn_camera(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsaction='Az4Fr:Jv50ub']").click()

    def btn_mic(self):
        self._driver.find_element(By.CSS_SELECTOR, "[jsaction='Az4Fr:Jv50ub']").click()

class GDriveDownloader(PageLoader):
    '''
    GDriveDownloader class is used to download a file from google drive.
    url: A google drive url to download
    download_folder: path to the folder where the file will be downloaded
    timeout: Time to wait for the page to load
    preferences: A list of tuples of (preference_name, preference_value) to set in the firefox profile
    '''
    def __init__(self, url: str=None, download_folder: str='./temp', timeout: int=20,
                 profile_path: str=None, preferences: list[tuple[str, str]]=None, addons: list[str]=None):
        # check if it is absolute path or relative path
        if not os.path.isabs(download_folder):
            download_folder = f'{os.getcwd()}/{download_folder}'
        if not download_folder.endswith('/'):
            download_folder = f'{download_folder}/'

        # check if download folder exists
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        super(GDriveDownloader, self).__init__((By.ID, 'uc-download-link'), timeout, profile_path,
                                               [('browser.download.folderList', 2),
                                                ('browser.download.dir', f'{download_folder}'),
                                                ('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')],
                                                addons)

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
    def __init__(self, url=None, timeout: int=20, profile_path: str=None,
                 preferences: list[tuple[str, str]]=None, addons: list[str]=None):
        super(GDocsPageLoader, self).__init__((By.CLASS_NAME, "gb_oe gb_Bc"), timeout,
                                              profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)
        self.strings = []

    def load(self, url) -> None:
        if 'docs.google.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid google docs url')

    def user(self, name, passwrd):
        self.name = name
        self.passwrd = passwrd

    def signin(self):
        # Input user account
        username = self._driver.find_element(By.ID, 'identifierId')
        username.send_keys(self.name)
        nextButton = self._driver.find_element(By.ID, 'identifierNext')
        nextButton.click()

        # Input user password
        password = self._driver.find_element(By.CSS_SELECTOR, "[aria-label='Enter your password']")
        password.send_keys(Keys.BACK_SPACE*20, self.passwrd)
        signInButton = self._driver.find_element(By.ID,'passwordNext')
        signInButton.click()

    def editor(self):
        # Create docs
        self._driver.find_element(By.CSS_SELECTOR, "[src='https://ssl.gstatic.com/docs/templates/thumbnails/docs-blank-googlecolors.png']").click()

        edit = self._driver.find_element(By.CSS_SELECTOR, "[class='kix-canvas-tile-content']")
        # self.strings = ['Khi', 'nhắc', 'lối', 'văn chương', 'khát khao', 'hướng', 'chân', '-', 'thiện', '-', 'mỹ', ',', 'ta', 'nhắc', 'Nguyễn Tuân', '-', 'nghệ sĩ', 'suốt', 'đời', 'đi', 'đẹp', 'Ông', 'bút', 'tài hoa văn học', 'Việt Nam', 'hiện đại', 'Trong', 'tác', 'Nguyễn Tuân', ',', 'nhân vật', 'miêu tả', ',', 'nghệ sĩ', 'Và', 'tác phẩm', '“', 'Chữ', 'tử tù', '”', 'xây dựng', 'vậy', 'Bên cạnh', 'đó', ',', 'văn', 'khéo léo', 'tình huống', 'truyện', 'vô', 'độc đáo', 'Đó', 'cảnh', 'chữ', 'giam', '-', 'đặc sắc', 'thiên truyện', '“', 'một', 'cảnh tượng', 'xưa', 'có', '”', '. Đoạn', 'chữ', 'nằm', 'tác phẩm', 'tình huống', 'truyện', 'đẩy', 'đỉnh', 'viên', 'quản ngục', 'công văn', 'xử tử', 'phản loạn', ',', 'Huấn', 'Cao', 'Do', 'cảnh', 'chữ nghĩa', 'cởi', 'nút', ',', 'giải tỏa', 'băn khoăn', ',', 'chờ đợi', 'đọc', ',', 'toát', 'lao', 'tác phẩm', 'công văn', ',', 'viên', 'quản ngục', 'giãi bày', 'tâm', 'thầy', 'thơ', 'lại', 'Nghe', 'xong', 'truyện', ',', 'thầy', 'thơ', 'chạy', 'buồng', 'giam', 'Huấn', 'Cao', 'nỗi', 'viên', 'quản ngục', 'Và', 'đêm', 'hôm', 'đó', ',', 'buồng tối', 'chật hẹp', 'ánh', 'đỏ rực', 'bó đuốc', 'tẩm', 'dầu', ',', '“', 'cảnh tượng', 'xưa', 'có', '”', 'diễn', 'ra', 'Thông', 'nghệ thuật', 'ta', 'gian', 'đẹp', ',', 'thoáng đãng', ',', 'yên tĩnh', 'Nhưng', 'gian', 'chứa', 'bóng tối', ',', 'nhơ bẩn', 'chốn', 'ngục tù', 'nghệ thuật', 'xảy', 'ra', 'Thời gian', 'gợi', 'ta', 'tình cảnh', 'tử tù', 'Đây', 'lẽ', 'đêm', 'tử', 'tù-người', 'chữ', 'phút', 'Huấn', 'Cao', 'Và', 'hoàn cảnh', '“', 'một', 'tù', 'cổ', 'đeo', 'gông', ',', 'chân', 'vướng', 'xiềng', '”', 'ung dung', ',', 'đĩnh đạc', '“', 'dậm', 'tô', 'nét', 'chữ', 'lụa', 'trắng tinh', '”', 'Trong', 'ấy', ',', 'viên', 'quản ngục', 'thầy', 'thơ', 'khúm', 'lúm', 'động', 'dường trật', 'xã hội', 'đảo lộn', 'Viên', 'quản ngục', 'nhẽ', 'hô hào', ',', 'răn đe', 'kẻ', 'tù tội', 'Thế', 'cảnh tượng', 'tù nhân', 'răn', 'dạy', ',', 'ban phát', 'đẹp', 'Đây', 'thực', 'gỡ', 'xưa', 'Huấn', 'Cao', '-', 'tài', 'viết', 'chữ', ',', 'đẹp', 'viên', 'quản ngục', ',', 'thầy', 'thơ', '-', 'chữ', 'Họ', 'hoàn cảnh', 'đặc biệt', ':', 'kẻ', 'phản nghịch', 'lĩnh', 'án', 'tử hình', '(', 'Huấn', 'Cao', ')', 'thực thi', 'pháp luật', 'Trên', 'bình diện', 'xã hội', ',', 'hai', 'đối lập', 'xét', 'bình diện', 'nghệ thuật', 'tri âm', ',', 'tri kỉ', 'nhau', 'Vì', 'chua xót', 'nhau', 'Hơn nữa', ',', 'thật', ',', 'ước', 'mình', 'Trong', 'đoạn', 'văn', ',', 'văn', 'tương phản ánh', 'bóng tối', 'câu', 'vận động', 'vận động', 'ánh', 'bóng tối', 'Cái', 'hỗn độn', ',', 'xô bồ', 'giam', 'khiết', 'lụa', 'trắng', 'nét', 'chữ', 'đẹp đẽ', 'Nhà văn', 'nổi bật', 'hình ảnh', 'Huấn', 'Cao', ',', 'tô', 'đậm', 'vươn', 'thắng', 'ánh', 'bóng tối', ',', 'đẹp', 'xấu', 'thiện ác', 'Vào', 'ấy', ',', 'quan hệ', 'đối nghịch', 'kì lạ', ':', 'lửa', 'nghĩa', 'bùng cháy', 'chốn', 'ngục tù', 'tối tăm', ',', 'đẹp', 'chốn', 'hôi hám', ',', 'nhơ bẩn', '…', 'đây', ',', 'Nguyễn Tuân', 'nêu bật', 'chủ đề', 'tác phẩm', ':', 'đẹp', 'chiến thắng', 'xấu xa', ',', 'thiên lương', 'chiến thắng', 'tội ác', 'Đó', 'tôn vinh', 'đẹp', ',', 'thiện', 'ấn tượng', 'chữ', 'xong', ',', 'Huấn', 'Cao', 'khuyên', 'quản ngục', 'chốn', 'ngục tù', 'nhơ bẩn', ':', '“', 'đổi', 'chỗ', 'ở', '”', 'sở nguyện', 'ý', 'Muốn', 'chữ', 'thiên lương', 'Trong', 'môi trường', 'ác', ',', 'đẹp', 'bền vững', 'Cái', 'đẹp', 'nảy sinh', 'chốn', 'tối tăm', ',', 'nhơ bẩn', ',', 'môi trường', 'ác', '(', 'chữ', 'tù', ') thể', 'sống', 'ác', 'Nguyễn Tuân nhắc', 'thú', 'chữ môn', 'nghệ thuật', 'đòi', 'cảm', 'thị giác', 'cảm', 'tâm hồn', 'Người ta', 'thưởng thức', 'mấy', 'thấy', ',', 'cảm', 'mùi', 'thơm', 'mực', 'Hãy', 'mực', 'chữ', 'hương vị', 'thiên lương', 'Cái', 'gốc', 'chữ', 'thiện', 'chữ', 'thể hiện', 'sống', 'văn hóa', 'khuyên', 'tử tù', ',', 'viên', 'quản ngục', 'xúc động', '“', 'vái', 'tù', 'vái', ',', 'chắp', 'câu', 'dòng', 'mắt', 'rỉ', 'kẽ', 'miệng', 'nghẹn ngào', ':', 'kẻ', 'mê muội', 'bái lĩnh', '”', 'Bằng', 'sức', 'nhân tài năng', 'xuất chúng', ',', 'tử tù', 'hướng', 'quản ngục', 'sống', 'thiện', 'Và', 'đường', 'chết', 'Huấn', 'Cao', 'gieo', 'mầm', 'sống', 'lầm đường', 'Trong', 'khung cảnh', 'đen tối', 'tù ngục', ',', 'hình tượng', 'Huấn', 'Cao', 'trở', 'thường', ',', 'dung tục', 'hèn', 'giới', 'xung quanh', 'Đồng thời', 'thể hiện', 'niềm', 'vững', 'người', ':', 'hoàn cảnh', 'khao khát', 'hướng', 'chân', '-', 'thiện-mỹ', '. Có', 'kiến', 'rằng', ':', 'Nguyễn Tuân', 'văn', 'mĩ', ',', 'tức', 'đẹp', ',', 'nghệ thuật', 'Nhưng', 'truyện ngắn', '“', 'Chữ', 'tử tù', '”', 'cảnh', 'chữ', 'ta', 'xét', 'hời hợt', ',', 'xác', 'Đúng', 'truyện ngắn', 'này', ',', 'Nguyễn Tuân', 'ca ngợi', 'đẹp', 'đẹp', 'bao', 'gắn', 'thiện', ',', 'thiên lương', 'người', 'Quan', 'định kiến', 'nghệ thuật', 'mạng', ',', 'Nguyễn Tuân văn', 'tư tưởng', 'mĩ', ',', 'quan', 'nghệ thuật', 'vị', 'nghệ thuật', 'Bên cạnh', 'đó', ',', 'truyện', 'ca ngợi', 'viên', 'quản ngục', 'thầy', 'thơ', 'sống', 'môi trường', 'độc ác', 'xấu', '“', 'thanh âm', 'trẻo', '”', 'hướng thiện', 'Qua', 'thể hiện', 'yêu', 'nước', ',', 'căm ghét', 'bọn', 'thống trị', 'đương thời', 'thái độ', 'trân trọng', 'đối', '“', 'thiên lương', '”', 'sở', 'đạo lí', 'truyền thống', 'văn', 'Chữ', 'tử tù', '”', 'ca', 'bi tráng', ',', 'bất diệt', 'thiên lương', ',', 'tài năng', 'nhân', 'người', 'Hành động', 'chữ', 'Huấn', 'Cao', ',', 'dòng', 'chữ', 'đời', 'nghĩa', 'truyền', 'tài hoa', 'kẻ', 'tri âm', ',', 'tri kỉ', 'hôm mai', 'sau', 'Nếu', 'truyền', 'đẹp', 'mai một', 'Đó', 'gìn', 'đẹp', 'đời', '. Bằng', 'nhịp điệu', 'chậm rãi', ',', 'câu văn', 'giàu', 'hình ảnh', 'gợi', 'liên tưởng', 'đoạn', 'phim', 'chậm', 'Từng', 'hình ảnh', ',', 'động tác', 'dần', 'hiện', 'ngòi bút', 'đậm', 'chất', 'điện ảnh', 'Nguyễn Tuân', ':', 'buồng tối', 'chật hẹp', '…', 'hình ảnh', '“', 'ba', 'đầu', 'chăm', 'lụa', 'trắng tinh', '”', ',', 'hình ảnh', 'tù', 'cổ', 'đeo', 'gông', ',', 'chân', 'vướng', 'xiềng', 'viết', 'chữ', 'Trình', 'miêu tả', 'thể hiện', 'tư tưởng', 'nét', ':', 'bóng tối', 'ánh sáng', ',', 'hôi hám', 'nhơ bẩn', 'đẹp', 'Ngôn ngữ', ',', 'hình ảnh', 'cổ kính', 'khí', 'tác phẩm', 'Ngôn ngữ', 'hán việt', 'miêu tả', 'đối tượng', 'thú', 'chữ', 'Tác giả', '“', 'phục chế', '”', 'cổ xưa', 'kĩ thuật', 'hiện đại', 'bút pháp', 'tả thực', ',', 'phân tích', 'tâm lí', 'nhân vật', '(', 'văn học', 'cổ', 'tả thực', 'phân tích', 'tâm lí', 'nhân vật', ')', '. Cảnh', 'chữ', '“', 'Chữ', 'tử tù', '”', 'kết tinh', 'tài năng', ',', 'tư tưởng', 'độc đáo', 'Nguyễn Tuân', 'Tác phẩm', 'ngưỡng vọng', 'tâm', 'nuối tiếc', 'đối', 'tài hoa', ',', 'nghĩa khí nhân', 'thượng', 'Đan xen', 'tác giả', 'kín', 'đao', 'bày tỏ', 'đau xót', 'đẹp', 'chân chính', ',', 'đích thực', 'hủy hoại', 'Tác phẩm', 'góp', 'tiếng', 'nhân bản', ':', 'đời', 'đen tối', 'tỏa', 'sáng']
        for i in range(0, len(self.strings)):
            ActionChains(self._driver).move_to_element(edit).click(edit).send_keys(self.strings[i] + " ").perform()
            time.sleep(1.5)

class GPhotosPageLoader(PageLoader):
    def __init__(self, url=None, timeout: int=20, profile_path: str=None,
                 preferences: list[tuple[str, str]]=None,  addons: list[str]=None):
        super(GPhotosPageLoader, self).__init__((By.CLASS_NAME, 'BiCYpc'), timeout,
                                                profile_path, preferences, addons)
        self.start_driver()
        if url:
            self.load(url)

    def load(self, url):
        if 'photos.google.com' in url:
            super().load(url)
        else:
            logging.error('Not a valid google photos url')

    def download(self) -> None:
        self._driver.find_element(By.CSS_SELECTOR, "[aria-label='More options']").click()
        self._driver.find_element(By.CSS_SELECTOR, "[aria-label='Download - Shift+D']").click()
