from django.apps import AppConfig
import os
import json

class StsvAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stsv_app"

    def ready(self):
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            if not firebase_admin._apps:
                firebase_creds_str = os.environ.get("FIREBASE_CREDENTIALS")
                
                if firebase_creds_str:
                    # Chuyển chuỗi JSON từ .env thành Dictionary
                    cert_dict = json.loads(firebase_creds_str)
                    cred = credentials.Certificate(cert_dict)
                    firebase_admin.initialize_app(cred)
                    print("Đã kết nối Firebase Admin bằng biến môi trường FIREBASE_CREDENTIALS thành công!")
                else:
                    print("Cảnh báo: Không tìm thấy biến FIREBASE_CREDENTIALS trong .env. Push Notification sẽ bị vô hiệu hóa.")
        except ImportError:
            print("Chưa cài đặt firebase-admin.")
        except Exception as e:
            print(f"Lỗi khi khởi tạo Firebase: {str(e)}")
