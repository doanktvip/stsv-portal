import random
import re
from stsv_app.models import StudentSemesterPoint, PointTransaction, TrainingCriterion, TrainingRule, TrainingRuleGroup, StudentProfile, Semester
from stsv_app.services import TrainingPointService


def seed_training_points():
    print("--- Nạp Dữ Liệu Điểm Rèn Luyện ---")

    
    RAW_TEXT = """
ĐIỀU 1 Điểm trần tối đa: 25đ Trách nhiệm chấp hành pháp luật và nội quy, quy chế của nhà trường Minh chứng chung cấp trường Mục 1: Sinh viên có điểm trung bình tích luỹ với thang điểm 4 cụ thể. Báo thiếu ID: 199 (12đ ) Từ 2,50 đến 3,19 Báo thiếu ID: 200 (13đ ) Từ 3,20 đến 3,59 Báo thiếu ID: 201 (14đ ) Từ 3,60 đến 4,00 Báo thiếu ID: 337 (10đ ) Dưới 1,99 Báo thiếu ID: 338 (11đ ) Từ 2,00 đến 2,49 Mục 2: Tham gia Hội thảo hoặc tọa đàm do Khoa hoặc Trường tổ chức Báo thiếu ID: 213 (3đ /Lần) Tham gia trực tiếp Báo thiếu ID: 8807 (1đ /Lần) Tham gia trực tuyến Mục 3: Là thành viên đội tuyển của nhà trường tham gia các cuộc thi học thuật với các đơn vị ngoài trường Báo thiếu ID: 228 (10đ /Học kỳ) Là thành viên Mục 4: Viết bài cho tạp chí của trường Báo thiếu ID: 229 (10đ /Lần) Viết tạp san Mục 5: Viết bài cho tập san, tạp chí ngoài trường Báo thiếu ID: 230 (10đ /Lần) Viết tạp san Mục 6: Tham gia đề tài NCKH cấp trường (Chỉ được tính 1 lần/đề tài) Báo thiếu ID: 231 (5đ /Lần) Tham gia Báo thiếu ID: 232 (10đ /Lần) Đạt giải đặc biệt, nhất, nhì Báo thiếu ID: 233 (7đ /Lần) Đạt giải ba, KK Mục 7: Tham gia Hội thảo hoặc Tọa đàm do các đơn vị ngoài trường tổ chức Báo thiếu ID: 471 (3đ /Lần) Tham gia trực tiếp Báo thiếu ID: 8808 (1đ /Lần) Tham gia trực tuyến Mục 8: Có giấy chứng nhận tham gia học các lớp chuyên đề kỹ năng học tập trong và ngoài trường Báo thiếu ID: 1978 (3đ /Học kỳ) Có giấy chứng nhận Mục 9: Thành viên các câu lạc bộ học thuật cấp khoa, trường Báo thiếu ID: 1982 (2đ /Học kỳ) Là thành viên Mục 10: Chương trình hướng nghiệp và phỏng vấn tuyển dụng: Phát triển nghề nghiệp cùng Swire Coca-Cola “Coke STEMX & STEPS" Báo thiếu ID: 4969 (3đ /Học kỳ) Tham gia Mục 11: Cuộc thi “Sinh viên với ý tưởng sáng tạo và khởi nghiệp” – năm 2025 Báo thiếu ID: 9428 (7đ /Học kỳ) Đạt giải I, II Báo thiếu ID: 9429 (5đ /Học kỳ) Đạt giải III, KK Báo thiếu ID: 9430 (2đ /Học kỳ) Cổ vũ bán kết - chung kết Báo thiếu ID: 10229 (3đ /Học kỳ) Tham gia
ĐIỀU 2 Điểm trần tối đa: 20đ Trách nhiệm, tinh thần và thái độ trong học tập Minh chứng chung cấp trường Mục 1: Có tham gia trong các buổi gặp gỡ trao đổi giữa nhà trường với SV, đóng góp về các hoạt động của nhà trường Báo thiếu ID: 263 (5đ /Học kỳ) Tham gia Mục 2: Sinh viên chấp hành quy chế thi tại trường Báo thiếu ID: 1209 (5đ /Học kỳ) Chấp hành Mục 3: Chấp hành Quy định của Thư Viện Báo thiếu ID: 1211 (5đ /Học kỳ) Chấp hành Báo thiếu ID: 1985 (-5đ /Học kỳ) Vi phạm Mục 4: Đóng học phí đúng hạn (Không có lệnh khóa MSSV trong học kỳ) Báo thiếu ID: 1212 (5đ /Học kỳ) Chấp hành Mục 5: Tham gia thực hiện phiếu phản hồi thông tin về môn học và giảng viên (đánh giá giảng viên trực tuyến) Báo thiếu ID: 1213 (10đ /Học kỳ) Chấp hành Mục 6: Thực hiện đăng ký ngoại trú Báo thiếu ID: 6881 (5đ /Học kỳ) Chấp hành Báo thiếu ID: 6882 (-5đ /Học kỳ) Vi phạm Mục 7: Sinh viên vi phạm Quy chế thi Báo thiếu ID: 1250 (-5đ /Học kỳ) Vi phạm Mục 8: Sinh hoạt lớp với Giáo viên chủ nhiệm, Cố vấn học tập Báo thiếu ID: 4651 (5đ /Học kỳ) Tham gia 
ĐIỀU 3 Điểm trần tối đa: 20đ Trách nhiệm tham gia các hoạt động chính trị - xã hội, văn hóa, văn nghệ, thể thao, phòng chống tội phạm, tệ nạn xã hội Minh chứng chung cấp trường Mục 1: Là thành viên các Câu lạc bộ sở thích, kỹ năng, thể dục thể thao ... cấp Khoa hoặc Trường Báo thiếu ID: 339 (2đ /Học kỳ) Tham gia Mục 2: Giao lưu văn hóa Việt Nam & Ấn Độ - Chào mừng 80 năm Quốc khánh Ấn Độ Báo thiếu ID: 341 (3đ /Học kỳ) Tham gia Báo thiếu ID: 342 (5đ /Học kỳ) Ban tổ chức Mục 3: Là thành viên đội tuyển TDTT, văn nghệ của Trường đang tham gia thi đấu giải cấp Thành phố trở lên Báo thiếu ID: 345 (10đ /Học kỳ) Tham gia Mục 4: Cuộc thi Người dẫn chương trình The Open Mic 2026 Báo thiếu ID: 351 (2đ /Học kỳ) Cổ vũ Báo thiếu ID: 352 (5đ /Học kỳ) Ban tổ chức Mục 5: Ngày hội việc làm năm 2026 Báo thiếu ID: 363 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10239 (5đ /Học kỳ) Hỗ trợ ban tổ chức Mục 6: Chương trình phát động cuộc thi và Talkshow “Cơ hội từ nghề nói” Báo thiếu ID: 413 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10240 (-3đ /Học kỳ) Đăng ký nhưng không tham gia Mục 7: Tham dự tuần lễ Sinh hoạt công dân SV đầu năm, đầu khóa. Báo thiếu ID: 564 (-10đ /Năm học) Không tham dự Báo thiếu ID: 1786 (10đ /Học kỳ) Tham dự Mục 8: Làm bài thu hoạch và giấy cam kết trong tuần lễ sinh hoạt công dân SV đầu năm, đầu khóa (cuối khóa) Báo thiếu ID: 1214 (4đ /Học kỳ) Có nộp Báo thiếu ID: 1258 (-4đ /Học kỳ) Không nộp hoặc làm bài thu hoạch không đạt Mục 9: Vở diễn "Yêu là thoát tội" Báo thiếu ID: 2769 (3đ /Học kỳ) Tham gia Báo thiếu ID: 2770 (3đ /Học kỳ) Tham gia ngày 23/10/2025 Mục 10: Lễ Khai giảng 05/9/2026 - Đối tượng tham dự: Chỉ dành cho Ban cán sự lớp Báo thiếu ID: 2945 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9427 (-3đ /Học kỳ) Đăng ký nhưng không tham gia Mục 11: BÌNH CHỌN DỰ ÁN YÊU THÍCH NHẤT - OU-STARTUP 2025 Báo thiếu ID: 2946 (3đ /Học kỳ) Tham gia Báo thiếu ID: 3440 (1đ /Học kỳ) Tham gia Mục 12: GIẢI BÓNG RỔ BỘ GIÁO DỤC VÀ ĐÀO TẠO 2025 Báo thiếu ID: 2947 (3đ /Học kỳ) Tham gia cổ vũ 18/10/2025 Báo thiếu ID: 3190 (10đ /Học kỳ) Thành viên đội tuyển Báo thiếu ID: 10339 (3đ /Học kỳ) Tham gia cổ vũ 21/10/2025 Báo thiếu ID: 10340 (3đ /Học kỳ) Tham gia cổ vũ 22/10/2025 Báo thiếu ID: 10341 (3đ /Học kỳ) Tham gia cổ vũ 25/10/2025 Mục 13: HỘI NGHỊ TẬP HUẤN VỀ CÔNG TÁC TUYÊN TRUYỀN, PHỔ BIẾN PHÁP LUẬT VÀ ỨNG DỤNG AI TRONG TRUYỀN THÔNG Báo thiếu ID: 2953 (3đ /Học kỳ) Tham gia buổi 1 Báo thiếu ID: 8850 (3đ /Học kỳ) Tham gia buổi 2 Mục 14: Tham gia Cổ vũ văn nghệ truyền thông Báo thiếu ID: 2954 (2đ /Học kỳ) Cổ vũ ngày 16/11/2025 Báo thiếu ID: 9436 (2đ /Học kỳ) Cổ vũ ngày 08/11/2025 Báo thiếu ID: 10105 (2đ /Học kỳ) Cổ vũ ngày 09/11/2025 Mục 15: CHƯƠNG TRÌNH “KẾT NỐI NGUỒN NHÂN LỰC VỚI NHÀ TUYỂN DỤNG” DO BÁO NGƯỜI LAO ĐỘNG TỔ CHỨC NĂM 2025 Báo thiếu ID: 2956 (3đ /Học kỳ) Tham gia buổi 1 Báo thiếu ID: 3601 (3đ /Học kỳ) Tham gia buổi 2 Mục 16: CHƯƠNG TRÌNH VIỆT NAM XANH Báo thiếu ID: 3600 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9893 (5đ /Học kỳ) Ban tổ chức Mục 17: THAM GIA MINIGAME THEO DẤU CHÂN BÁC Báo thiếu ID: 3007 (1đ /Học kỳ) Tham gia Báo thiếu ID: 3008 (5đ /Học kỳ) Ban tổ chức Mục 18: CHIẾU PHIM NÂNG CAO NHẬN THỨC CỦA SINH VIÊN Báo thiếu ID: 3015 (3đ /Học kỳ) Buổi 4/12/2025 Báo thiếu ID: 3188 (3đ /Học kỳ) Buổi 5/12/2025 Báo thiếu ID: 3189 (3đ /Học kỳ) Buổi 11/12/2025 Báo thiếu ID: 3597 (3đ /Học kỳ) Buổi 21/11/2025 Báo thiếu ID: 4654 (3đ /Học kỳ) Buổi 15/12/2025 Báo thiếu ID: 10230 (3đ /Học kỳ) Buổi 16/12/2025 Báo thiếu ID: 10231 (3đ /Học kỳ) Buổi 17/12/2025 Báo thiếu ID: 10232 (3đ /Học kỳ) Buổi 18/12/2025 Báo thiếu ID: 10233 (3đ /Học kỳ) Buổi 22/12/2025 Báo thiếu ID: 10234 (3đ /Học kỳ) Buổi 23/12/2025 Báo thiếu ID: 10235 (3đ /Học kỳ) Buổi 24/12/2025 Báo thiếu ID: 10236 (3đ /Học kỳ) Buổi 25/12/2025 Báo thiếu ID: 10237 (3đ /Học kỳ) Buổi 26/12/2025 Báo thiếu ID: 10238 (3đ /Học kỳ) Buổi 19/12/2025 Báo thiếu ID: 10412 (3đ /Học kỳ) Buổi 29/12/2025 Báo thiếu ID: 10413 (3đ /Học kỳ) Buổi 30/12/2025 Báo thiếu ID: 10414 (3đ /Học kỳ) Buổi 31/12/2025 Mục 19: Cuộc thi Bình chọn Nhà tuyển dụng được yêu thích 2025 Báo thiếu ID: 3260 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10547 (7đ /Học kỳ) Đoạt giải I, II Báo thiếu ID: 10548 (5đ /Học kỳ) Đoạt giải III, KK Mục 20: Chương trình Debut Mentoring mùa 4 Báo thiếu ID: 3261 (3đ /Học kỳ) Tham gia Mục 21: CHƯƠNG TRÌNH OU FEST Báo thiếu ID: 3262 (3đ /Học kỳ) Tham gia Báo thiếu ID: 5033 (3đ /Học kỳ) TALKSHOW SINH SẢN Báo thiếu ID: 5990 (1đ /Học kỳ) OU VIBE MINIGAME TUẦN 2 Báo thiếu ID: 8929 (5đ /Học kỳ) Ban tổ chức Mục 22: HỘI THẢO: “TRADEEXPO – TRIỂN LÃM GIAO THƯƠNG TRÊN NỀN TẢNG SỐ B2B” Báo thiếu ID: 3264 (3đ /Học kỳ) Tham gia Mục 23: Chương trình “NGÀY HỘI KHỞI NGHIỆP CÔNG NGHIỆP VĂN HÓA” Báo thiếu ID: 3315 (3đ /Học kỳ) Tham gia Mục 24: HOẠT ĐỘNG TRỰC TUYẾN MYSTICODE Báo thiếu ID: 3316 (1đ /Học kỳ) Tham gia Báo thiếu ID: 3343 (2đ /Học kỳ) Ban tổ chức Báo thiếu ID: 4567 (5đ /Học kỳ) Webinar: Hỏi đáp cùng chuyên gia - Kỹ năng phỏng vấn thành công. Thời gian: 10/01/2022 Báo thiếu ID: 6084 (5đ /Học kỳ) Webinar: Cơ hội nghề nghiệp ngành CNTT tại TMA Solutions. Thời gian: 12/01/2022 Báo thiếu ID: 6085 (5đ /Học kỳ) Webinar: Job opportunities in Edtech for non-tech Students. Thời gian: 14/01/2022 Báo thiếu ID: 6086 (5đ /Học kỳ) Tham gia chuyên đề Chủ đề: "TRỞ LẠI TRƯỜNG HỌC AN TOÀN SAU ĐẠI DỊCH COVID-19", ngày 11/2/2022 Mục 25: Cuộc thi Just Be Nice Báo thiếu ID: 3318 (1đ /Học kỳ) Tham gia vòng 1 Báo thiếu ID: 3356 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 8851 (7đ /Học kỳ) Đạt giải I, II Báo thiếu ID: 8852 (5đ /Học kỳ) Đạt giải III, KK Báo thiếu ID: 10342 (3đ /Học kỳ) Tham gia vòng 2 Báo thiếu ID: 10343 (5đ /Học kỳ) Tham gia vòng chung kết Báo thiếu ID: 10344 (2đ /Học kỳ) Cổ vũ Mục 26: CHƯƠNG TRÌNH HỌP MẶT CÁN BỘ ĐOÀN BAN CÁN SỰ THPT TRÚNG TUYỂN VÀO TRƯỜNG NĂM HỌC 2025 - 2026 Báo thiếu ID: 3319 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9442 (5đ /Học kỳ) Ban tổ chức Mục 27: Tập huấn sơ cấp cứu năm 2025 Báo thiếu ID: 3320 (3đ /Học kỳ) Tham gia Mục 28: Tổ chức buổi chiếu phim giao lưu quốc tế với đoàn giáo sư, sinh viên Đại học Newcastle, Úc và giảng viên, sinh viên Trường Đại học Mở TPHCM (Khoa Đào tạo đặc biệt) Báo thiếu ID: 3325 (3đ /Học kỳ) Tham gia Mục 29: chương trình Chia sẻ thực tiễn từ doanh nghiệp, chủ đề “Chuyển đổi số: Sinh viên chuẩn bị gì cho hành trang lập nghiệp?” Báo thiếu ID: 3326 (3đ /Học kỳ) Tham gia Mục 30: Chương trình Chia sẻ thực tiễn từ doanh nghiệp, chủ đề “Khởi nghiệp hay Lập nghiệp: Lựa chọn nào cho Gene Z?” Báo thiếu ID: 3327 (3đ /Học kỳ) Tham gia Mục 31: Khảo sát do phòng Công tác sinh viên và Truyền thông phụ trách Báo thiếu ID: 4559 (5đ /Học kỳ) Tham gia khảo sát đánh giá sự hài lòng của người học về công tác tiếp sinh viên, triển khai giải quyết các thủ tục hành chính thông thường liên quan sinh viên Báo thiếu ID: 4560 (3đ /Học kỳ) Tham gia Khảo sát sự hài lòng của người học trước tốt nghiệp - năm học 2024 - 2025 Báo thiếu ID: 4561 (5đ /Học kỳ) Tham gia khảo sát sự hài lòng của người học về triển khai xét – cấp học bổng sinh viên Báo thiếu ID: 4562 (5đ /Học kỳ) Tham gia Khảo sát sự hài lòng của người học về việc tham gia các hoạt động ngoại khóa sinh viên Báo thiếu ID: 4563 (1đ /Học kỳ) Tham gia khảo sát sự hài lòng của sinh viên đối với công tác Cố vấn học tập - Chủ nhiệm lớp Báo thiếu ID: 4570 (1đ /Học kỳ) khảo sát tân sinh viên phục vụ công tác hướng nghiệp khóa 2025 Báo thiếu ID: 7433 (3đ /Học kỳ) Khảo sát tổng hợp thông tin nhu cầu tìm việc làm phục vụ công tác giới thiệu cho người học năm cuối - Năm học 2024 - 2025 Báo thiếu ID: 7900 (3đ /Học kỳ) khảo sát bộ dữ liệu thông tin sinh viên làm thêm, làm việc ngoài giờ, thời vụ cho sinh viên khóa 2022, 2023, 2024, 2025 - NH 25 - 26 Mục 32: CHƯƠNG TRÌNH MENTORING Báo thiếu ID: 3834 (3đ /Học kỳ) Tháng 11/2025 Báo thiếu ID: 5064 (3đ /Học kỳ) Tháng 12/2025 Báo thiếu ID: 8972 (3đ /Học kỳ) Tháng 01/2026 Báo thiếu ID: 9476 (3đ /Học kỳ) Tham gia tháng 8 Mục 33: Tham gia Workshop Báo thiếu ID: 3835 (3đ /Học kỳ) Workshop “Kết nối qua sắc đỏ” - Quốc khánh Vương quốc Campuchia Báo thiếu ID: 5062 (3đ /Học kỳ) “Sắc màu văn hóa - Hương vị Lào” Báo thiếu ID: 5063 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 10346 (3đ /Học kỳ) Chào mừng Ngày Nhà giáo Việt Nam 20_11 Mục 34: CHƯƠNG TRÌNH TUYÊN DƯƠNG CÔNG DÂN TRẺ TIÊU BIỂU THÀNH PHỐ HỒ CHÍ MINH Báo thiếu ID: 3836 (7đ /Học kỳ) Ban tổ chức Báo thiếu ID: 4242 (5đ /Học kỳ) Tham gia Mục 35: THAM GIA CHƯƠNG TRÌNH 50 NĂM TUYÊN DƯƠNG THƠ NHẠC CẤT CÁNH CÙNG THÀNH PHỐ Báo thiếu ID: 3837 (5đ /Học kỳ) Tham gia Báo thiếu ID: 6582 (7đ /Học kỳ) Ban tổ chức Mục 36: THAM GIA TẬP HUẤN CÁN BỘ ĐOÀN HỘI Báo thiếu ID: 3838 (3đ /Học kỳ) THAM GIA TẬP HUẤN CÁN BỘ ĐOÀN HỘI CẤP KHOA Báo thiếu ID: 7190 (3đ /Học kỳ) THAM GIA TẬP HUẤN CÁN BỘ ĐOÀN - HỘI CẤP CHI Mục 37: CHUỖI HOẠT ĐỘNG HÀNH TRÌNH THEO DẤU CHÂN BÁC Báo thiếu ID: 3850 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 3863 (3đ /Học kỳ) Tham gia WORKSHOP Báo thiếu ID: 3864 (1đ /Học kỳ) Tham gia - Người giữ lửa Mục 38: khảo sát sự hài lòng của người học đối với hoạt động của các đơn vị phục vụ đào tạo - hệ đại học chính quy năm 2025 Báo thiếu ID: 3841 (5đ /Học kỳ) Tham gia Mục 39: THAM GIA HOẠT ĐỘNG GIAO LƯU NHÂN DỊP KỶ NIỆM NGÀY THÀNH LẬP QUÂN ĐỘI NHÂN DÂN VIỆT NAM Báo thiếu ID: 3842 (3đ /Học kỳ) Tham gia Báo thiếu ID: 5052 (7đ /Học kỳ) Ban tổ chức Mục 40: THAM GIA LỄ KHỞI CÔNG DỰ ÁN XÂY DỰNG NHÀ VĂN HÓA THANH NIÊN Báo thiếu ID: 3844 (5đ /Học kỳ) Tham gia Báo thiếu ID: 3862 (5đ /Học kỳ) Ban tổ chức Mục 41: THAM GIA LỄ TRAO GIẢI TUỔI TRẺ STARTUP AWARD 2025 Báo thiếu ID: 3845 (5đ /Học kỳ) Tham gia Báo thiếu ID: 8864 (5đ /Học kỳ) Ban tổ chức Mục 42: LỚP CÁC BÀI LÝ LUẬN CHÍNH TRỊ NĂM HỌC 2025 - 2026 Báo thiếu ID: 3846 (5đ /Học kỳ) Không gian ngày Hội Báo thiếu ID: 3847 (5đ /Học kỳ) Báo cáo Chuyên đề: Kỹ năng đổi mới sáng tạo trong khởi nghiệp đối với sinh viên Báo thiếu ID: 3848 (5đ /Học kỳ) Hoàn thành Báo thiếu ID: 3849 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 6589 (3đ /Học kỳ) Tham gia Mục 43: THAM GIA LỄ TRAO GIẢI TUỔI TRẺ STARTUP AWARD 2025 Báo thiếu ID: 3851 (5đ /Học kỳ) Tham gia Mục 44: ĐOÀN VIÊN CHUYỂN SINH HOẠT ĐOÀN TRÊN ỨNG DỤNG THANH NIÊN VIỆT NAM Báo thiếu ID: 3853 (3đ /Học kỳ) Tham gia Báo thiếu ID: 3854 (5đ /Học kỳ) Ban tổ chức Mục 45: THAM GIA NHỮNG NGÀY VĂN HỌC TP HỒ CHÍ MINH Báo thiếu ID: 3857 (5đ /Học kỳ) Tham gia Mục 46: HỌP MẶT CÁN BỘ ĐOÀN HỘI CUỐI NĂM - MỪNG XUÂN BÍNH NGỌ 2026 Báo thiếu ID: 3859 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9766 (5đ /Học kỳ) BAN TỔ CHỨC Mục 47: THAM GIA ĐỒNG DIỄN KHÁT VỌNG SINH VIÊN Báo thiếu ID: 3860 (1đ /Học kỳ) Tham gia Mục 48: CUỘC THI TRỰC TUYẾN CHESS QUEST Báo thiếu ID: 3868 (1đ /Học kỳ) Tham gia Báo thiếu ID: 9769 (2đ /Học kỳ) Ban tổ chức Mục 49: THAM GIA NGÀY HỘI CÔNG DÂN TOÀN CẦU Báo thiếu ID: 3873 (5đ /Học kỳ) Tham gia Mục 50: CHƯƠNG TRÌNH VINH DANH THỦ KHOA NĂM 2025 Báo thiếu ID: 3878 (5đ /Học kỳ) Tham gia Mục 51: THAM GIA HỌP GIAO BAN ĐOÀN - HỘI CÁC CẤP HỌC KỲ I Báo thiếu ID: 4245 (3đ /Học kỳ) Tham gia Báo thiếu ID: 4568 (5đ /Học kỳ) Ban tổ chức Mục 52: THAM GIA DIỄN ĐÀN LẮNG NGHE SINH VIÊN NÓI VỀ MỨC SINH THẤP TẠI TP HỒ CHÍ MINH NĂM 2025 Báo thiếu ID: 4247 (5đ /Học kỳ) Tham gia Mục 53: THAM GIA HÀNH TRÌNH ĐOÀN VIÊN ƯU TÚ Báo thiếu ID: 4331 (3đ /Học kỳ) Tham gia Mục 54: THAM GIA NGÀY HỘI THE OPEN CLUB 2026 Báo thiếu ID: 4967 (3đ /Học kỳ) THAM GIA NGÀY HỘI Báo thiếu ID: 7091 (3đ /Học kỳ) THAM GIA ĐÊM NHẠC HỘI Báo thiếu ID: 7093 (5đ /Học kỳ) Ban tổ chức Mục 55: NGÀY HỘI TẾT DÂN TỘC MỞ RỘNG VÒNG TAY NĂM 2026 Báo thiếu ID: 4970 (3đ /Học kỳ) Tham gia ngày hội Tết dân tộc Báo thiếu ID: 6078 (3đ /Học kỳ) Tham gia đêm nhạc Tết Dân tộc Báo thiếu ID: 8181 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 8182 (5đ /Học kỳ) CUỘC THI TRANG PHỤC DÂN TỘC - TẾT DÂN TỘC 2024 Báo thiếu ID: 8183 (7đ /Học kỳ) Ban tổ chức Mục 56: Báo cáo chuyên đề Tầm quan trọng của Thái độ học tập tích cực Báo thiếu ID: 8809 (3đ /Học kỳ) Tham gia Báo thiếu ID: 8810 (3đ /Lần) Ban tổ chức Mục 57: GIẢI BÓNG RỔ ĐẠI HỘI TDTT PHƯỜNG XUÂN HÒA 2025 Báo thiếu ID: 8969 (10đ /Học kỳ) Tham gia Mục 58: Tình nguyện viên tham gia phục vụ Giải Tiền Phong Half Marathon 2025 Báo thiếu ID: 8970 (1đ /Học kỳ) Tham gia Mục 59: Chuyên đề: Tuổi trẻ chung vai - Vì tương lai không còn dịch bệnh AIDS Báo thiếu ID: 8971 (3đ /Học kỳ) Tham gia Mục 60: Chuyên đề tâm lý: "Thế giới số - Gắn kết thật hay ảo tưởng thân quen" Báo thiếu ID: 8973 (3đ /Học kỳ) Tham gia Mục 61: THAM GIA HỖ TRỢ CÔNG TÁC CHUẨN BỊ ĐẠI HỘI ĐOÀN THÀNH PHỐ Báo thiếu ID: 8974 (3đ /Học kỳ) Tham gia Báo thiếu ID: 8975 (5đ /Học kỳ) Tham gia Mục 62: Chuyên đề 81 năm ngày thành lập Quân đội Nhân dân Việt Nam Báo thiếu ID: 8976 (3đ /Học kỳ) Tham gia Mục 63: CẢM TÌNH ĐOÀN ĐỢT 1 NĂM HỌC 2025 - 2026 Báo thiếu ID: 8977 (3đ /Học kỳ) Tham gia Đạt Báo thiếu ID: 8978 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 10353 (-3đ /Học kỳ) Vắng không tham gia Mục 64: HỘI THẢO THÀNH PHỐ HỒ CHÍ MINH: TẦM NHÌN MỚI, KHÁT VỌNG MỚI Báo thiếu ID: 8979 (3đ /Học kỳ) Tham gia Mục 65: HỘI THẢO BIẾN RÁC THẢI THÀNH NĂNG LƯỢNG SẠCH: GIẢI PHÁP CHO PHÁT TRIỂN BỀN VỮNG Báo thiếu ID: 8980 (3đ /Học kỳ) Tham gia Mục 66: SINH VIÊN THAM GIA WORKSHOP BÁO PHỤ NỮ Báo thiếu ID: 8981 (3đ /Học kỳ) Tham gia Mục 67: Hành trình về nguồn - Dấu ấn Việt Nam Báo thiếu ID: 9010 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9011 (5đ /Học kỳ) Ban tổ chức Mục 68: MiniGame Báo thiếu ID: 9163 (1đ /Học kỳ) Chào mừng Kỷ niệm 78 năm Ngày Độc lập Cộng hòa Liên bang Myanmar Báo thiếu ID: 9164 (1đ /Học kỳ) Chào mừng tân sinh viên quốc tế nhập học năm học 2025-2026 Báo thiếu ID: 10345 (2đ /Học kỳ) Ban tổ chức Mục 69: Nghệ thuật xiết - hành trình kết nối Báo thiếu ID: 9165 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9166 (5đ /Học kỳ) Ban tổ chức Mục 70: THAM GIA CHƯƠNG TRÌNH GIAO LƯU VỚI LỮ ĐOÀN PHÁO BINH 434 Báo thiếu ID: 9170 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10347 (5đ /Học kỳ) Ban tổ chức Mục 71: THAM GIA HỌC TẬP QUÁN TRIỆT NGHỊ QUYẾT TRỌNG TÂM CỦA ĐẢNG BAN HÀNH NĂM 2025 Báo thiếu ID: 9171 (3đ /Học kỳ) Tham gia Mục 72: THAM GIA SINH HOẠT CLB LÝ LUẬN TRẺ Báo thiếu ID: 9175 (2đ /Học kỳ) Cổ vũ Báo thiếu ID: 9176 (3đ /Học kỳ) Tham gia tháng 11/2025 Báo thiếu ID: 9488 (3đ /Học kỳ) Tham gia tháng 12/2025 Báo thiếu ID: 9489 (3đ /Học kỳ) Tham gia tháng 1/2026 Báo thiếu ID: 9490 (5đ /Học kỳ) Giải III, KK Mục 73: NGÀY HỘI MÔI TRƯỜNG 2026 Báo thiếu ID: 9179 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9180 (5đ /Học kỳ) Ban tổ chức Mục 74: THAM GIA GÓP Ý HIẾN KẾ CÁC GIẢI PHÁP MÔ HÌNH Ý TƯỞNG TRONG LĨNH VỰC KHOA HỌC CÔNG NGHỆ ĐỔI MỚI SÁNG TẠO VÀ CHUYỂN ĐỔI SỐ Báo thiếu ID: 9182 (3đ /Học kỳ) Tham gia Mục 75: Chương trình giao lưu văn hóa - nghệ thuật tại Nhà hát Trần Hữu Trang Báo thiếu ID: 9184 (3đ /Học kỳ) Tham gia Mục 76: Xanh giữa lòng phố - Chạm vào thiên nhiên Báo thiếu ID: 9185 (3đ /Học kỳ) Tham gia Báo thiếu ID: 9186 (5đ /Học kỳ) Ban tổ chức Mục 77: GIẢI CỜ VUA ĐẠI HỌC Y DƯỢC MỞ RỘNG TSOC_s Báo thiếu ID: 10357 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10358 (2đ /Học kỳ) Cổ vũ Mục 78: THAM GIA GIẢI VÔ ĐỊCH CÁC CÂU LẠC BỘ CỜ VUA SINH VIÊN TP.HCM MỞ RỘNG Báo thiếu ID: 10365 (5đ /Học kỳ) Tham gia Mục 79: MINIGAME BIẾT MÁU HIỂU MÁU Báo thiếu ID: 10368 (1đ /Học kỳ) Tham gia Báo thiếu ID: 10369 (2đ /Học kỳ) Ban tổ chức Mục 80: CHƯƠNG TRÌNH ÁNH SÁNG LÝ LUẬN TRẺ Báo thiếu ID: 10372 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10373 (5đ /Học kỳ) Ban tổ chức Mục 81: TALKSHOW TỰ TIN HỘI NHẬP KHẲNG ĐỊNH BẢN SẮC RIÊNG Báo thiếu ID: 10376 (3đ /Học kỳ) Tham gia Báo thiếu ID: 10377 (5đ /Học kỳ) Ban tổ chức Mục 82: LỄ CHÀO CỜ HƯỚNG VỀ ĐẠI HỘI ĐẢNG TOÀN QUỐC LẦN THỨ XIV CỦA ĐẢNG CỘNG SẢN VIỆT NAM Báo thiếu ID: 10379 (5đ /Học kỳ) Tham gia Mục 83: TALKSHOW "WHO AM I!?" Báo thiếu ID: 10600 (3đ /Học kỳ) Tham gia Mục 84: CUỘC THI TRỰC TUYẾN "SINH VIEN OU - ỨNG XỬ CHUẨN GU" Báo thiếu ID: 10601 (1đ /Học kỳ) Tham gia Mục 85: MINIGAME X TO SEEK Báo thiếu ID: 10602 (1đ /Học kỳ) Tham gia Báo thiếu ID: 10603 (3đ /Học kỳ) Ban tổ chức Mục 86: CUỘC THI TÌM HIỂU VỀ 80 NĂM NGÀY TỔNG TUYỂN CỬ ĐẦU TIÊN BẦU QUỐC HỘI VIỆT NAM Báo thiếu ID: 10604 (1đ /Học kỳ) Tham gia Tuần 18 Báo thiếu ID: 10605 (1đ /Học kỳ) Tham gia Tuần 19 Mục 87: Báo cáo chuyên đề: “Hình mẫu sinh viên thế hệ mới” năm 2026 Báo thiếu ID: 10656 (3đ /Học kỳ) Tham gia Mục 88: HỖ TRỢ CUỘC THI TUYÊN TRUYỀN PHÒNG CHỐNG MUA BÁN NGƯỜI Báo thiếu ID: 11107 (5đ /Học kỳ) Tham gia Minh chứng cấp khoa (trong trường) Mục 1: Sinh hoạt công dân - Chuyên đề 2 tại Khoa Báo thiếu ID: 3962 (3đ /Học kỳ) Tham gia Báo thiếu ID: 3976 (5đ /Học kỳ) Ban tổ chức Minh chứng cấp khoa (ngoài trường) Mục 1: CHƯƠNG TRÌNH NGOÀI TRƯỜNG Báo thiếu ID: 3856 (3đ /Học kỳ) Tham gia chương trình "Ươm mầm tri thức" III 2025 Báo thiếu ID: 4224 (3đ /Học kỳ) Chương trình Ngày làm việc tốt 
ĐIỀU 4 Điểm trần tối đa: 15đ Trách nhiệm công dân trong quan hệ cộng đồng Minh chứng chung cấp trường Mục 1: Hiến máu tình nguyện Báo thiếu ID: 305 (10đ /Lần) Tham gia Báo thiếu ID: 306 (10đ /Lần) Ban tổ chức Mục 2: Tham dự chiến dịch tình nguyện Mùa hè xanh: Báo thiếu ID: 10638 (10đ /Lần) Tham gia Báo thiếu ID: 10639 (10đ /Lần) Ban tổ chức Mục 3: Tham dự chương trình "Thứ 7 tình nguyện" Báo thiếu ID: 310 (3đ /Học kỳ) Cấp Chi Báo thiếu ID: 311 (5đ /Học kỳ) Cấp Khoa/Trường Mục 4: CHƯƠNG TRÌNH TRI ÂN VÀ PHỤC VỤ CỘNG ĐỒNG OU THANKS 2025 Báo thiếu ID: 313 (3đ /Học kỳ) Tham gia Báo thiếu ID: 314 (5đ /Học kỳ) Ban tổ chức Báo thiếu ID: 8675 (10đ /Học kỳ) Quán quân, Á quân Mục 5: Tham dự chương trình "Ngày chủ nhật xanh" Báo thiếu ID: 316 (3đ /Lần) Tham gia Báo thiếu ID: 317 (5đ /Lần) Ban tổ chức Mục 6: Tham dự chương trình "Trung thu" Báo thiếu ID: 319 (7đ /Học kỳ) Tham gia Báo thiếu ID: 5478 (7đ /Học kỳ) Ban tổ chức Mục 7: Sinh viên có hành vi tốt, có tinh thần sẻ chia, giúp đỡ người khó khăn hoạn nạn được tuyên dương bằng văn bản Báo thiếu ID: 324 (5đ /Lần) Sinh viên có hành vi tốt Báo thiếu ID: 1993 (-5đ /Lần) Sinh viên có hành vi chưa tốt có văn bản phê bình Mục 8: Sinh viên chấp hành pháp luật và các quy định của Nhà nước không có thông báo do công an hoặc các đơn vị khác gửi cho Trường Báo thiếu ID: 1217 (10đ /Học kỳ) Tham gia Báo thiếu ID: 1992 (-5đ /Học kỳ) Vi phạm Mục 9: Công trình Thanh niên Báo thiếu ID: 3259 (3đ /Học kỳ) Cấp Chi Báo thiếu ID: 5021 (5đ /Học kỳ) Cấp Khoa/Trường Mục 10: THAM GIA HOẠT ĐỘNG ĐỘI HÌNH TÌNH NGUYỆN SỐ Báo thiếu ID: 3875 (3đ /Học kỳ) SV THAM GIA ÍT Báo thiếu ID: 10606 (5đ /Học kỳ) SV THAM GIA VỪA Báo thiếu ID: 10607 (7đ /Học kỳ) SV THAM GIA NHIỀU Báo thiếu ID: 10608 (7đ /Học kỳ) Ban tổ chức Mục 11: THAM GIA QUYÊN GÓP CHƯƠNG TRÌNH ÁO ẤM CHO EM Báo thiếu ID: 3876 (1đ /Học kỳ) QUYÊN GÓP ÍT Báo thiếu ID: 4709 (3đ /Học kỳ) QUYÊN GÓP NHIỀU Báo thiếu ID: 9491 (5đ /Học kỳ) BAN TỔ CHỨC Mục 12: Sinh viên đạt giấy khen tham gia tích cực hoạt động "Vì nụ cười trẻ thơ" Báo thiếu ID: 3877 (3đ /Học kỳ) Tham gia Mục 13: BEACH CLEANUP DAY 2025 Báo thiếu ID: 4244 (3đ /Học kỳ) Tham gia Báo thiếu ID: 7780 (5đ /Học kỳ) Ban tổ chức Mục 14: Hiến tóc Báo thiếu ID: 4966 (10đ /Học kỳ) Tham gia Mục 15: Tham gia Xuân tình nguyện Báo thiếu ID: 7196 (7đ /Học kỳ) Tham gia Báo thiếu ID: 7197 (7đ /Học kỳ) Ban tổ chức Mục 16: THAM GIA HỖ TRỢ TIẾP NHẬN VẬT PHẨM ỦNG HỘ KHẮC PHỤC BÃO LŨ TẠI NHÀ VH THANH NIÊN Báo thiếu ID: 10384 (3đ /Học kỳ) Tham gia
ĐIỀU 5 Điểm trần tối đa: 20đ Đánh giá về ý thức và kết quả tham gia phụ trách lớp học, các đoàn thể, tổ chức khác trong nhà trường Minh chứng chung cấp trường Mục 1: Bằng cấp, giấy khen... Báo thiếu ID: 331 (10đ ) SV đạt giải I, II cấp thành phố, khu vực; đạt giải I, II, III, Khuyến khích cấp toàn quốc về học tập, NCKH Báo thiếu ID: 332 (10đ ) SV được tặng Bằng khen của UBND Tỉnh, Thành phố (trực thuộc TW) về các hoạt động chính trị, văn hóa – xã hội, thể thao, phòng chống tệ nạn xã hội, giữ gìn trật tự xã hội, cứu người… Mục 2: Đạt danh hiệu Đoàn viên ưu tú Báo thiếu ID: 302 (5đ ) Đạt danh hiệu Mục 3: Các chức vụ bao gồm: Ban cán sự lớp, Ban chấp hành các cấp bộ Đoàn, Hội (trường, khoa, lớp), Chi ủy CB SV, Ban chủ nhiệm các Câu lạc bộ học thuật, sở thích, kỹ năng, thể dục thể thao... của Khoa hoặc Trường (chỉ tính chức vụ tham gia công tác cao nhất): Báo thiếu ID: 1218 (10đ /Học kỳ) Hoàn thành tốt nhiệm vụ Báo thiếu ID: 1219 (5đ /Học kỳ) Hoàn thành nhiệm vụ Báo thiếu ID: 1220 (0đ /Học kỳ) Không hoàn hành nhiệm vụ Mục 4: SV được tặng Bằng khen, Giấy khen các cấp của Đoàn TNCS HCM, Hội sinh viên Việt Nam, Hội liên hiệp Thanh niên Việt Nam Báo thiếu ID: 10141 (10đ /Học kỳ) Trực Thuộc Cấp TW, tỉnh, Thành Báo thiếu ID: 10142 (5đ /Học kỳ) Trực thuộc phường, xã và tương đương
ĐIỀU 6 Điểm trần tối đa: 10đ Các trường hợp đặc biệt Minh chứng chung cấp trường Mục 1: Đảng viên đạt thành tích: Báo thiếu ID: 1976 (10đ /Học kỳ) Hoàn thành Xuất sắc nhiệm vụ Báo thiếu ID: 2000 (7đ /Học kỳ) Hoàn thành tốt nhiệm vụ Báo thiếu ID: 2001 (5đ /Học kỳ) Hoàn thành nhiệm vụ Mục 2: Sinh viên khuyết tật, tàn tật, mồ côi cả cha lẫn mẹ hoặc cha hoặc mẹ, hoàn cảnh gia đình đặc biệt khó khăn có xác nhận của địa phương (Sinh viên nộp hồ sơ một lần vào đầu khóa học (riêng đối với giấy xác nhận gia đình đặc biệt khó khăn có xác nhận của địa phương nộp hàng năm) đạt mức điểm trung bình học tập tích lũy: Báo thiếu ID: 1995 (7đ /Học kỳ) Từ 2,00 đến 2,49 Báo thiếu ID: 1996 (8đ /Học kỳ) Từ 2,50 đến 3,19 Báo thiếu ID: 1997 (9đ /Học kỳ) Từ 3,20 đến 3,59 Báo thiếu ID: 1998 (10đ /Học kỳ) Từ 3,60 đến 4,00 Mục 3: SV được kết nạp Đảng hoặc chuyển Đảng chính thức (chỉ được cộng 1 lần duy nhất trong 4 năm học chính khoá) Báo thiếu ID: 8815 (10đ ) SV được kết nạp Đảng hoặc chuyển Đảng chính thức (chỉ được cộng 1 lần duy nhất trong 4 năm học chính khoá)
"""
    
    current_criterion = None

    # Xoá data cũ
    TrainingRule.objects.all().delete()
    TrainingRuleGroup.objects.all().delete()
    TrainingCriterion.objects.all().delete()

    lines = RAW_TEXT.split('\n')
    CRITERIA_RULES = []

    def parse_rules_in_line(line_text, criterion):
        group_matches = list(re.finditer(r"(Mục \d+:.*?)(?= Mục \d+:|$)", line_text))
        for g in group_matches:
            group_text = g.group(1).strip()
            parts = group_text.split(" Báo thiếu ID: ", 1)
            group_name = parts[0].strip()
            if len(group_name) > 255:
                group_name = group_name[:252] + "..."
            
            is_single = "điểm trung bình" in group_name.lower() or "chức vụ" in group_name.lower()

            group, _ = TrainingRuleGroup.objects.get_or_create(
                criterion=criterion,
                name=group_name,
                defaults={"is_single_choice": is_single}
            )
            
            if len(parts) > 1:
                rules_text = "Báo thiếu ID: " + parts[1]
                rules = re.finditer(r"Báo thiếu ID: (\d+) \((-?\d+)đ .*?\) (.*?)(?= Báo thiếu ID: |$)", rules_text)
                for r in rules:
                    TrainingRule.objects.create(
                        code=r.group(1),
                        description=r.group(3).strip(),
                        points=int(r.group(2)),
                        criterion=criterion,
                        group=group,
                        is_proof_required=(int(r.group(2)) > 0)
                    )
                    CRITERIA_RULES.append({"code": r.group(1), "points": int(r.group(2)), "description": r.group(3).strip()})
        
        # Nếu không có Mục nào nhưng vẫn có Báo thiếu ID (ngoại lệ)
        if not group_matches:
            rules = re.finditer(r"Báo thiếu ID: (\d+) \((-?\d+)đ .*?\) (.*?)(?= Báo thiếu ID: | Mục \d+: |$)", line_text)
            for r in rules:
                TrainingRule.objects.create(
                    code=r.group(1),
                    description=r.group(3).strip(),
                    points=int(r.group(2)),
                    criterion=criterion,
                    is_proof_required=(int(r.group(2)) > 0)
                )
                CRITERIA_RULES.append({"code": r.group(1), "points": int(r.group(2)), "description": r.group(3).strip()})

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("ĐIỀU"):
            match = re.match(r"(ĐIỀU \d+) Điểm trần tối đa: (\d+)đ", line)
            if match:
                c_name = match.group(1)
                c_max = int(match.group(2))
                current_criterion, _ = TrainingCriterion.objects.get_or_create(
                    name=c_name,
                    defaults={"max_points": c_max}
                )
                rule_text = line[match.end():]
                parse_rules_in_line(rule_text, current_criterion)
        else:
            if current_criterion:
                parse_rules_in_line(line, current_criterion)

    for c in TrainingCriterion.objects.all():
        TrainingRule.objects.create(
            code=f"EVENT_C{c.id}",
            description="Điểm cộng tự động từ các Sự kiện đã tham gia",
            points=100,
            criterion=c,
            is_proof_required=False,
            is_event_rule=True
        )

    students = list(StudentProfile.objects.all())
    semesters = list(Semester.objects.all())
    if not students or not semesters:
        return

    # Filter out empty students
    students = [s for s in students if s.user.is_active]

    # 1. Tạo Transactions và Minh chứng trước
    print("Đang nạp các giao dịch điểm rèn luyện và minh chứng...")
    transactions_to_create = []
    
    for student in students:
        for semester in semesters:
            for criterion in TrainingCriterion.objects.prefetch_related('groups__rules', 'rules').all():
                # Xử lý các nhóm (Groups)
                for group in criterion.groups.all():
                    valid_rules = [r for r in group.rules.all() if r.points > 0 and not r.is_event_rule]
                    if not valid_rules:
                        continue
                    
                    if group.is_single_choice:
                        # Với nhóm Single-Choice (chọn 1): Chỉ chọn tối đa 1 quy tắc (xác suất 60%)
                        if random.random() < 0.6:
                            chosen_rule = random.choice(valid_rules)
                            status = random.choice([
                                PointTransaction.Status.APPROVED, 
                                PointTransaction.Status.AUTO_APPROVED
                            ])
                            transactions_to_create.append(PointTransaction(
                                student=student,
                                semester=semester,
                                rule=chosen_rule,
                                points_changed=chosen_rule.points,
                                reason=f"Đã nộp minh chứng tham gia: {chosen_rule.description}",
                                proof_image="https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=600&auto=format&fit=crop",
                                status=status
                            ))
                    else:
                        # Với nhóm Multiple-Choice: Chọn ngẫu nhiên 0 - 2 quy tắc
                        if random.random() < 0.4:
                            k_sample = min(random.randint(1, 2), len(valid_rules))
                            for rule in random.sample(valid_rules, k=k_sample):
                                status = random.choice([
                                    PointTransaction.Status.APPROVED, 
                                    PointTransaction.Status.AUTO_APPROVED
                                ])
                                transactions_to_create.append(PointTransaction(
                                    student=student,
                                    semester=semester,
                                    rule=rule,
                                    points_changed=rule.points,
                                    reason=f"Đã nộp minh chứng tham gia: {rule.description}",
                                    proof_image="https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=600&auto=format&fit=crop",
                                    status=status
                                ))
                
                # Xử lý các quy tắc đứng độc lập (không thuộc group nào)
                standalone_rules = [r for r in criterion.rules.all() if r.group_id is None and r.points > 0 and not r.is_event_rule]
                if standalone_rules and random.random() < 0.3:
                    chosen_rule = random.choice(standalone_rules)
                    status = random.choice([
                        PointTransaction.Status.APPROVED, 
                        PointTransaction.Status.AUTO_APPROVED
                    ])
                    transactions_to_create.append(PointTransaction(
                        student=student,
                        semester=semester,
                        rule=chosen_rule,
                        points_changed=chosen_rule.points,
                        reason=f"Đã nộp minh chứng tham gia: {chosen_rule.description}",
                        proof_image="https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=600&auto=format&fit=crop",
                        status=status
                    ))

    if transactions_to_create:
        PointTransaction.objects.bulk_create(transactions_to_create)

    # 2. Tính toán StudentSemesterPoint với dữ liệu phong phú (rich nested points_data)
    print("Đang tổng hợp bảng điểm rèn luyện sinh viên theo học kỳ...")
    
    for student in students:
        service = TrainingPointService(student.user)
        for semester in semesters:
            point = service.calculate_student_points(semester, student_profile=student)
            # Ngẫu nhiên trạng thái DRAFT hoặc SUBMITTED
            if random.random() < 0.4:
                point.status = StudentSemesterPoint.Status.SUBMITTED
                point.save(update_fields=['status'])

    print("Nạp dữ liệu điểm rèn luyện thành công.")

