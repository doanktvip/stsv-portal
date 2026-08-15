import requests
import json

# Đổi cổng này nếu Server Django của bạn chạy ở cổng khác
BASE_URL = "http://127.0.0.1:8000"

# Hãy điền tài khoản và mật khẩu mà bạn đang có sẵn trong Database vào đây
TEST_ACCOUNTS = {
    "ADMIN": {"username": "admin", "password": "123456"},          # Sửa lại username/password cho đúng
    "STUDENT": {"username": "giaovu_cntt", "password": "123456"},      # Sửa lại username/password
    "LECTURER": {"username": "GV_CNTT_01", "password": "123456"},        # Sửa lại username/password
    "ORGOFFICER": {"username": "K25_7480101_01", "password": "123456"}# Sửa lại username/password
}

def test_login_and_get_me(role, credentials):
    print(f"\n{'='*50}")
    print(f"🚀 ĐANG TEST ROLE: {role}")
    print(f"{'='*50}")

    # 1. Gọi API Login để lấy Token
    login_url = f"{BASE_URL}/auth/login"
    try:
        login_res = requests.post(login_url, json=credentials)
        
        if login_res.status_code != 200:
            print(f"❌ Đăng nhập thất bại ({login_res.status_code}). Vui lòng kiểm tra lại tài khoản/mật khẩu.")
            print("Chi tiết:", login_res.text)
            return

        login_data = login_res.json()
        access_token = None
        if "data" in login_data and isinstance(login_data["data"], dict):
            access_token = login_data["data"].get("access") or login_data["data"].get("access_token") or login_data["data"].get("token")
        
        if not access_token:
            access_token = login_data.get("access") or login_data.get("access_token") or login_data.get("token")
             
        if not access_token:
            print("❌ Không tìm thấy access_token trong kết quả trả về của API Login.")
            print(json.dumps(login_data, indent=2, ensure_ascii=False))
            return
            
        print("✅ Đăng nhập thành công! Đã lấy được Access Token.")
        
        # 2. Gọi API /users/me/
        me_url = f"{BASE_URL}/users/me/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        me_res = requests.get(me_url, headers=headers)
        
        print("\n📥 KẾT QUẢ /users/me/:")
        if me_res.status_code == 200:
            print(json.dumps(me_res.json(), indent=4, ensure_ascii=False))
        else:
            print(f"❌ API /users/me/ bị lỗi với mã {me_res.status_code}")
            print(me_res.text)

    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối tới Server. Hãy chắc chắn rằng bạn đã chạy 'python manage.py runserver'.")

if __name__ == "__main__":
    print("BẮT ĐẦU TEST CÁC ROLE TRONG HỆ THỐNG...\n")
    for role, credentials in TEST_ACCOUNTS.items():
        test_login_and_get_me(role, credentials)
    print("\nHOÀN TẤT TEST!")
