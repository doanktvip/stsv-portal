# stsv-portal

## Hướng dẫn cài đặt và khởi chạy (Dành cho Windows)

### 1. Kích hoạt môi trường ảo (Virtual Environment)
Môi trường ảo của dự án được đặt trong thư mục `venv`. Để kích hoạt, hãy mở terminal (Powershell hoặc CMD) tại thư mục gốc của dự án (`d:\stsv-portal`) và chạy lệnh sau:

**Nếu dùng Powershell:**
```powershell
.\venv\Scripts\Activate.ps1
```
*(Lưu ý: Nếu gặp lỗi Execution Policy, hãy chạy lệnh `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` trước)*

**Nếu dùng Command Prompt (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

---

### 2. Chạy ứng dụng
Sau khi kích hoạt môi trường ảo thành công (có chữ `(venv)` ở đầu dòng lệnh), di chuyển vào thư mục code và khởi động server:
```powershell
cd stsv_project
python manage.py runserver
```

---

### 3. Cập nhật cơ sở dữ liệu
Bất cứ khi nào có thay đổi về Model, hãy chạy các lệnh sau để đồng bộ xuống Database:
```powershell
cd stsv_project
python manage.py makemigrations
python manage.py migrate
```

---

### 4. Nạp dữ liệu ảo (Seeding)
Dùng để tạo dữ liệu mẫu cho môi trường phát triển. **Chỉ chạy được khi `DEBUG=True`.**

```powershell
cd stsv_project

# Nạp dữ liệu với số lượng mặc định (50 sinh viên, 20 sự kiện)
python manage.py seed

# Xoá toàn bộ dữ liệu cũ rồi nạp lại từ đầu
python manage.py seed --clear

# Tuỳ chỉnh số lượng sinh viên và sự kiện
python manage.py seed --students 100 --events 50

# Kết hợp: xoá sạch + nạp lại với số lượng tuỳ chỉnh
python manage.py seed --clear --students 100 --events 50
```

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| `--clear` | _(không có)_ | Xoá toàn bộ dữ liệu trước khi nạp |
| `--students` | `50` | Số lượng sinh viên cần tạo |
| `--events` | `20` | Số lượng sự kiện cần tạo |

---

## Lệnh Test & Kiểm tra độ phủ code (Coverage)

> Tất cả lệnh dưới đây chạy từ thư mục `stsv_project` với môi trường ảo đã được kích hoạt.

### 5. Chạy test

```powershell
cd stsv_project

# Chạy toàn bộ test
python manage.py test

# Chạy test với output chi tiết
python manage.py test --verbosity=2

# Chỉ chạy test của một app cụ thể
python manage.py test stsv_app

# Chỉ chạy một file test cụ thể
python manage.py test stsv_app.tests.test_momo

# Chỉ chạy một test case cụ thể
python manage.py test stsv_app.tests.test_momo.MoMoProviderTestCase.test_generate_payment_url_success
```

---

### 6. Đo độ phủ code (Coverage)

```powershell
cd stsv_project

# Chạy toàn bộ test + đo coverage, in báo cáo ra terminal (hay dùng nhất)
coverage run manage.py test && coverage report -m

# Tạo báo cáo HTML (mở file htmlcov/index.html bằng trình duyệt để xem trực quan)
coverage html

# Chỉ chạy coverage cho một số file test cụ thể
coverage run manage.py test stsv_app.tests.test_momo stsv_app.tests.test_vnpay

# Xem lại báo cáo lần chạy gần nhất (không chạy lại test)
coverage report
```

> **Cấu hình coverage** nằm tại [`stsv_project/.coveragerc`](./stsv_project/.coveragerc).  
> Các thư mục tự động bị loại trừ: `migrations/`, `seeders/`, `manage.py`, `*/apps.py`, `*/management/*`.

---

### 7. Kết quả mục tiêu

| Chỉ số | Mục tiêu |
|--------|----------|
| Tests passed | ✅ 162/162 (0 failures) |
| Code coverage | ✅ 100% |