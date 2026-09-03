import logging
logger = logging.getLogger(__name__)

class PushNotificationService:
    @staticmethod
    def send_push_notification(user, title, body, data=None):
        """
        Gửi Push Notification qua Firebase Cloud Messaging.
        Hàm này sử dụng try-except để không làm crash hệ thống 
        khi chưa cấu hình Firebase.
        """
        try:
            import firebase_admin
            from firebase_admin import messaging
            
            # Kiểm tra xem Firebase đã được khởi tạo chưa
            if not firebase_admin._apps:
                logger.warning("Firebase Admin chưa được cấu hình. Push Notification bị bỏ qua.")
                return False

            devices = user.devices.exclude(fcm_token__isnull=True).exclude(fcm_token="")
            
            if not devices.exists():
                return False
                
            tokens = list(devices.values_list('fcm_token', flat=True))
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens,
            )
            
            # Sử dụng send_each_for_multicast thay cho send_multicast (đã bị xóa ở bản mới)
            response = messaging.send_each_for_multicast(message)
            logger.info(f"Đã gửi {response.success_count} push notifications tới người dùng {user.username}")
            return response.success_count > 0
            
        except ImportError:
            logger.warning("Thư viện firebase-admin chưa được cài đặt. Push Notification bị bỏ qua.")
            return False
        except Exception as e:
            logger.error(f"Lỗi khi gửi Push Notification: {str(e)}")
            return False

    @staticmethod
    def send_to_multiple_users(users, title, body, data=None):
        """
        Hàm hỗ trợ gửi push notification cho nhiều người dùng cùng lúc.
        """
        for user in users:
            PushNotificationService.send_push_notification(user, title, body, data)
