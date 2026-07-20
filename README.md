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

### 2. Chạy ứng dụng
Sau khi kích hoạt môi trường ảo thành công (có chữ `(venv)` ở đầu dòng lệnh), bạn di chuyển vào thư mục code và khởi động server:
```powershell
cd stsv_project
python manage.py runserver
```

### 3. Cập nhật cơ sở dữ liệu
Bất cứ khi nào có thay đổi về Model, hãy chạy các lệnh sau để đồng bộ xuống Database:
```powershell
cd stsv_project
python manage.py makemigrations
python manage.py migrate
```