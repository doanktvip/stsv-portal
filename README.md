# 🎓 Hệ thống Sổ tay Sinh viên (Student Handbook App)

Dự án Hệ thống Sổ tay Sinh viên là một ứng dụng di động hỗ trợ sinh viên số hóa các hoạt động ngoại khóa. Tính năng cốt lõi của ứng dụng là **Tự động theo dõi và tính toán Điểm rèn luyện**, tích hợp thuật toán "Chặn điểm trần" theo đúng quy chế nhà trường và hỗ trợ **Điểm danh sự kiện nhanh chóng bằng mã QR**.

---

## 🏗️ Kiến trúc Hệ thống

Dự án được chia thành 2 phân hệ chính:
- **Backend (`stsv_project`)**: Xây dựng bằng Python, Django MVT và Django REST Framework. Sử dụng hệ quản trị CSDL MySQL và Elasticsearch.
- **Frontend Mobile (`stsv_app_mobile`)**: Ứng dụng di động đa nền tảng (Android/iOS) được xây dựng bằng Flutter, ứng dụng kiến trúc Riverpod để quản lý State.

---

## ⚙️ Yêu cầu Hệ thống (Prerequisites)

Trước khi bắt đầu cài đặt, đảm bảo máy tính của bạn đã được thiết lập:
- **Python 3.10+**
- **Flutter SDK 3.x**
- Hệ quản trị CSDL MySQL (hoặc sử dụng qua XAMPP/Docker)

---

## 🚀 I. Hướng dẫn cài đặt Backend (Django API)

Các bước dưới đây giúp bạn khởi chạy máy chủ API nội bộ (Localhost). Hãy mở Terminal (PowerShell hoặc CMD) tại thư mục gốc của dự án.

### 1. Kích hoạt môi trường ảo (Virtual Environment)
Môi trường ảo giúp cách ly các thư viện của dự án để tránh xung đột. Chạy lệnh sau:

**Dành cho PowerShell (Windows):**
```powershell
.\venv\Scripts\Activate.ps1
```
*(Mẹo: Nếu gặp lỗi quyền thực thi "Execution Policy", hãy mở PowerShell bằng quyền Administrator và chạy lệnh: `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`)*

**Dành cho Command Prompt (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

### 2. Khởi tạo Cơ sở Dữ liệu (Migrations)
Đảm bảo bạn đã tạo Database trong MySQL theo cấu hình tại file `.env`. Sau đó, áp dụng cấu trúc CSDL từ code xuống database thực tế:
```powershell
cd stsv_project
python manage.py makemigrations
python manage.py migrate
```

### 3. Nạp dữ liệu giả lập (Seeding)
Hệ thống cung cấp sẵn lệnh tự động nạp dữ liệu mẫu (Quy chế điểm, Sự kiện, Sinh viên, Giao dịch) giúp bạn có ngay dữ liệu để test app.
*(Lưu ý: Chỉ khả dụng khi biến cấu hình môi trường `DEBUG=True`)*
```powershell
# Nạp dữ liệu mặc định (50 sinh viên, 20 sự kiện)
python manage.py seed

# Tuỳ chỉnh số lượng nạp (100 sinh viên, 50 sự kiện)
python manage.py seed --students 100 --events 50

# Xoá trắng toàn bộ dữ liệu cũ và nạp lại từ đầu
python manage.py seed --clear
```

### 4. Khởi chạy Máy chủ (Run Server)
```powershell
python manage.py runserver
```
🎉 **Thành công!** Máy chủ API lúc này sẽ hoạt động tại địa chỉ: `http://127.0.0.1:8000/`

---

## 📱 II. Hướng dẫn cài đặt Frontend (Flutter Mobile App)

### 1. Cài đặt thư viện Dart
Mở một cửa sổ Terminal **mới** (không tắt terminal đang chạy Backend), trỏ vào thư mục ứng dụng di động và tải thư viện:
```powershell
cd stsv_app_mobile
flutter pub get
```

### 2. Khởi chạy Ứng dụng
Đảm bảo bạn đã bật máy ảo (Android Emulator / iOS Simulator) hoặc đã cắm cáp kết nối điện thoại vật lý vào máy tính:
```powershell
flutter run
```

---

## 🧪 III. Kiểm thử và Độ phủ Mã nguồn (Testing & Coverage)

*(Tài liệu này dành cho lập trình viên Backend)*

Đảm bảo bạn đã kích hoạt môi trường ảo (`venv`) và đang đứng tại thư mục `stsv_project`.

### 1. Chạy Unit Test
Hệ thống sở hữu bộ Unit Test hoàn chỉnh giúp bảo vệ tính toàn vẹn của logic.
```powershell
# Chạy toàn bộ Test Case
python manage.py test

# Chạy Test Case và hiển thị chi tiết nguyên nhân lỗi (nếu có)
python manage.py test --verbosity=2

# Chỉ định chạy test cho thư mục app cụ thể
python manage.py test stsv_app
```

### 2. Kiểm tra Độ phủ Mã nguồn (Test Coverage)
Đo lường tỉ lệ code đã được kiểm thử để đảm bảo độ tin cậy của ứng dụng (Hiện tại dự án đạt chuẩn **100% Coverage**):
```powershell
# 1. Chạy kiểm thử đồng thời thu thập dữ liệu độ phủ, in kết quả ra Terminal
coverage run manage.py test && coverage report -m

# 2. Xuất báo cáo HTML trực quan (để xem chi tiết code cover từng dòng)
coverage html
```
*(Mẹo: Mở file `htmlcov/index.html` bằng trình duyệt web để xem giao diện báo cáo HTML)*