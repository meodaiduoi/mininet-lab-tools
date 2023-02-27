# config and environment
import tomli
import sys, os
import logging
import pandas as pd

try:
    with open('config.toml', 'rb') as f:
        config = tomli.load(f)
        interface = config['enviroment']['interface']
        store_path = config['enviroment']['store_path']
        url_list = config['gg-docs']['url_list']
        
        # To load module from parent folder
        sys.path.insert(1, '../' )
except FileNotFoundError:
    logging.critical('Config file not found')
    os._exit(1)

# Code start from here
from webcapture.pcapcapture import *
from webcapture.ggservice import GDocsPageLoader
        
if __name__ == '__main__':
    try:
        # Create timestamp

        # Save ssl key to file
        os.environ['SSLKEYLOGFILE'] = './output/Docs_sslkey_{timestamp}.log'

        # Load docs
        docs = GDocsPageLoader("")
        docs.user("account","passwrd")
        docs.signin()

        # Start capture
        capture = AsyncQUICTrafficCapture()
        capture.capture(interface, './output/Docs_{timestamp}.pcap')
        # Example docs.strings = ['Khi', 'nhắc', 'lối', 'văn chương', 'khát khao', 'hướng', 'chân', '-', 'thiện', '-', 'mỹ', ',', 'ta', 'nhắc', 'Nguyễn Tuân', '-', 'nghệ sĩ', 'suốt', 'đời', 'đi', 'đẹp', 'Ông', 'bút', 'tài hoa văn học', 'Việt Nam', 'hiện đại', 'Trong', 'tác', 'Nguyễn Tuân', ',', 'nhân vật', 'miêu tả', ',', 'nghệ sĩ', 'Và', 'tác phẩm', '“', 'Chữ', 'tử tù', '”', 'xây dựng', 'vậy', 'Bên cạnh', 'đó', ',', 'văn', 'khéo léo', 'tình huống', 'truyện', 'vô', 'độc đáo', 'Đó', 'cảnh', 'chữ', 'giam', '-', 'đặc sắc', 'thiên truyện', '“', 'một', 'cảnh tượng', 'xưa', 'có', '”', '. Đoạn', 'chữ', 'nằm', 'tác phẩm', 'tình huống', 'truyện', 'đẩy', 'đỉnh', 'viên', 'quản ngục', 'công văn', 'xử tử', 'phản loạn', ',', 'Huấn', 'Cao', 'Do', 'cảnh', 'chữ nghĩa', 'cởi', 'nút', ',', 'giải tỏa', 'băn khoăn', ',', 'chờ đợi', 'đọc', ',', 'toát', 'lao', 'tác phẩm', 'công văn', ',', 'viên', 'quản ngục', 'giãi bày', 'tâm', 'thầy', 'thơ', 'lại', 'Nghe', 'xong', 'truyện', ',', 'thầy', 'thơ', 'chạy', 'buồng', 'giam', 'Huấn', 'Cao', 'nỗi', 'viên', 'quản ngục', 'Và', 'đêm', 'hôm', 'đó', ',', 'buồng tối', 'chật hẹp', 'ánh', 'đỏ rực', 'bó đuốc', 'tẩm', 'dầu', ',', '“', 'cảnh tượng', 'xưa', 'có', '”', 'diễn', 'ra', 'Thông', 'nghệ thuật', 'ta', 'gian', 'đẹp', ',', 'thoáng đãng', ',', 'yên tĩnh', 'Nhưng', 'gian', 'chứa', 'bóng tối', ',', 'nhơ bẩn', 'chốn', 'ngục tù', 'nghệ thuật', 'xảy', 'ra', 'Thời gian', 'gợi', 'ta', 'tình cảnh', 'tử tù', 'Đây', 'lẽ', 'đêm', 'tử', 'tù-người', 'chữ', 'phút', 'Huấn', 'Cao', 'Và', 'hoàn cảnh', '“', 'một', 'tù', 'cổ', 'đeo', 'gông', ',', 'chân', 'vướng', 'xiềng', '”', 'ung dung', ',', 'đĩnh đạc', '“', 'dậm', 'tô', 'nét', 'chữ', 'lụa', 'trắng tinh', '”', 'Trong', 'ấy', ',', 'viên', 'quản ngục', 'thầy', 'thơ', 'khúm', 'lúm', 'động', 'dường trật', 'xã hội', 'đảo lộn', 'Viên', 'quản ngục', 'nhẽ', 'hô hào', ',', 'răn đe', 'kẻ', 'tù tội', 'Thế', 'cảnh tượng', 'tù nhân', 'răn', 'dạy', ',', 'ban phát', 'đẹp', 'Đây', 'thực', 'gỡ', 'xưa', 'Huấn', 'Cao', '-', 'tài', 'viết', 'chữ', ',', 'đẹp', 'viên', 'quản ngục', ',', 'thầy', 'thơ', '-', 'chữ', 'Họ', 'hoàn cảnh', 'đặc biệt', ':', 'kẻ', 'phản nghịch', 'lĩnh', 'án', 'tử hình', '(', 'Huấn', 'Cao', ')', 'thực thi', 'pháp luật', 'Trên', 'bình diện', 'xã hội', ',', 'hai', 'đối lập', 'xét', 'bình diện', 'nghệ thuật', 'tri âm', ',', 'tri kỉ', 'nhau', 'Vì', 'chua xót', 'nhau', 'Hơn nữa', ',', 'thật', ',', 'ước', 'mình', 'Trong', 'đoạn', 'văn', ',', 'văn', 'tương phản ánh', 'bóng tối', 'câu', 'vận động', 'vận động', 'ánh', 'bóng tối', 'Cái', 'hỗn độn', ',', 'xô bồ', 'giam', 'khiết', 'lụa', 'trắng', 'nét', 'chữ', 'đẹp đẽ', 'Nhà văn', 'nổi bật', 'hình ảnh', 'Huấn', 'Cao', ',', 'tô', 'đậm', 'vươn', 'thắng', 'ánh', 'bóng tối', ',', 'đẹp', 'xấu', 'thiện ác', 'Vào', 'ấy', ',', 'quan hệ', 'đối nghịch', 'kì lạ', ':', 'lửa', 'nghĩa', 'bùng cháy', 'chốn', 'ngục tù', 'tối tăm', ',', 'đẹp', 'chốn', 'hôi hám', ',', 'nhơ bẩn', '…', 'đây', ',', 'Nguyễn Tuân', 'nêu bật', 'chủ đề', 'tác phẩm', ':', 'đẹp', 'chiến thắng', 'xấu xa', ',', 'thiên lương', 'chiến thắng', 'tội ác', 'Đó', 'tôn vinh', 'đẹp', ',', 'thiện', 'ấn tượng', 'chữ', 'xong', ',', 'Huấn', 'Cao', 'khuyên', 'quản ngục', 'chốn', 'ngục tù', 'nhơ bẩn', ':', '“', 'đổi', 'chỗ', 'ở', '”', 'sở nguyện', 'ý', 'Muốn', 'chữ', 'thiên lương', 'Trong', 'môi trường', 'ác', ',', 'đẹp', 'bền vững', 'Cái', 'đẹp', 'nảy sinh', 'chốn', 'tối tăm', ',', 'nhơ bẩn', ',', 'môi trường', 'ác', '(', 'chữ', 'tù', ') thể', 'sống', 'ác', 'Nguyễn Tuân nhắc', 'thú', 'chữ môn', 'nghệ thuật', 'đòi', 'cảm', 'thị giác', 'cảm', 'tâm hồn', 'Người ta', 'thưởng thức', 'mấy', 'thấy', ',', 'cảm', 'mùi', 'thơm', 'mực', 'Hãy', 'mực', 'chữ', 'hương vị', 'thiên lương', 'Cái', 'gốc', 'chữ', 'thiện', 'chữ', 'thể hiện', 'sống', 'văn hóa', 'khuyên', 'tử tù', ',', 'viên', 'quản ngục', 'xúc động', '“', 'vái', 'tù', 'vái', ',', 'chắp', 'câu', 'dòng', 'mắt', 'rỉ', 'kẽ', 'miệng', 'nghẹn ngào', ':', 'kẻ', 'mê muội', 'bái lĩnh', '”', 'Bằng', 'sức', 'nhân tài năng', 'xuất chúng', ',', 'tử tù', 'hướng', 'quản ngục', 'sống', 'thiện', 'Và', 'đường', 'chết', 'Huấn', 'Cao', 'gieo', 'mầm', 'sống', 'lầm đường', 'Trong', 'khung cảnh', 'đen tối', 'tù ngục', ',', 'hình tượng', 'Huấn', 'Cao', 'trở', 'thường', ',', 'dung tục', 'hèn', 'giới', 'xung quanh', 'Đồng thời', 'thể hiện', 'niềm', 'vững', 'người', ':', 'hoàn cảnh', 'khao khát', 'hướng', 'chân', '-', 'thiện-mỹ', '. Có', 'kiến', 'rằng', ':', 'Nguyễn Tuân', 'văn', 'mĩ', ',', 'tức', 'đẹp', ',', 'nghệ thuật', 'Nhưng', 'truyện ngắn', '“', 'Chữ', 'tử tù', '”', 'cảnh', 'chữ', 'ta', 'xét', 'hời hợt', ',', 'xác', 'Đúng', 'truyện ngắn', 'này', ',', 'Nguyễn Tuân', 'ca ngợi', 'đẹp', 'đẹp', 'bao', 'gắn', 'thiện', ',', 'thiên lương', 'người', 'Quan', 'định kiến', 'nghệ thuật', 'mạng', ',', 'Nguyễn Tuân văn', 'tư tưởng', 'mĩ', ',', 'quan', 'nghệ thuật', 'vị', 'nghệ thuật', 'Bên cạnh', 'đó', ',', 'truyện', 'ca ngợi', 'viên', 'quản ngục', 'thầy', 'thơ', 'sống', 'môi trường', 'độc ác', 'xấu', '“', 'thanh âm', 'trẻo', '”', 'hướng thiện', 'Qua', 'thể hiện', 'yêu', 'nước', ',', 'căm ghét', 'bọn', 'thống trị', 'đương thời', 'thái độ', 'trân trọng', 'đối', '“', 'thiên lương', '”', 'sở', 'đạo lí', 'truyền thống', 'văn', 'Chữ', 'tử tù', '”', 'ca', 'bi tráng', ',', 'bất diệt', 'thiên lương', ',', 'tài năng', 'nhân', 'người', 'Hành động', 'chữ', 'Huấn', 'Cao', ',', 'dòng', 'chữ', 'đời', 'nghĩa', 'truyền', 'tài hoa', 'kẻ', 'tri âm', ',', 'tri kỉ', 'hôm mai', 'sau', 'Nếu', 'truyền', 'đẹp', 'mai một', 'Đó', 'gìn', 'đẹp', 'đời', '. Bằng', 'nhịp điệu', 'chậm rãi', ',', 'câu văn', 'giàu', 'hình ảnh', 'gợi', 'liên tưởng', 'đoạn', 'phim', 'chậm', 'Từng', 'hình ảnh', ',', 'động tác', 'dần', 'hiện', 'ngòi bút', 'đậm', 'chất', 'điện ảnh', 'Nguyễn Tuân', ':', 'buồng tối', 'chật hẹp', '…', 'hình ảnh', '“', 'ba', 'đầu', 'chăm', 'lụa', 'trắng tinh', '”', ',', 'hình ảnh', 'tù', 'cổ', 'đeo', 'gông', ',', 'chân', 'vướng', 'xiềng', 'viết', 'chữ', 'Trình', 'miêu tả', 'thể hiện', 'tư tưởng', 'nét', ':', 'bóng tối', 'ánh sáng', ',', 'hôi hám', 'nhơ bẩn', 'đẹp', 'Ngôn ngữ', ',', 'hình ảnh', 'cổ kính', 'khí', 'tác phẩm', 'Ngôn ngữ', 'hán việt', 'miêu tả', 'đối tượng', 'thú', 'chữ', 'Tác giả', '“', 'phục chế', '”', 'cổ xưa', 'kĩ thuật', 'hiện đại', 'bút pháp', 'tả thực', ',', 'phân tích', 'tâm lí', 'nhân vật', '(', 'văn học', 'cổ', 'tả thực', 'phân tích', 'tâm lí', 'nhân vật', ')', '. Cảnh', 'chữ', '“', 'Chữ', 'tử tù', '”', 'kết tinh', 'tài năng', ',', 'tư tưởng', 'độc đáo', 'Nguyễn Tuân', 'Tác phẩm', 'ngưỡng vọng', 'tâm', 'nuối tiếc', 'đối', 'tài hoa', ',', 'nghĩa khí nhân', 'thượng', 'Đan xen', 'tác giả', 'kín', 'đao', 'bày tỏ', 'đau xót', 'đẹp', 'chân chính', ',', 'đích thực', 'hủy hoại', 'Tác phẩm', 'góp', 'tiếng', 'nhân bản', ':', 'đời', 'đen tối', 'tỏa', 'sáng']
        docs.strings = ['']
        docs.editor()

        # Turn off capture and driver
        capture.terminate()
        docs.close_driver()

    except KeyboardInterrupt:
        logging.error('Keyboard Inter')
        sys.exit()