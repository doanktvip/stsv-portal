from .base import BaseService
from stsv_app.models.system import SystemConfig, NotificationTemplate, UserNotification
from .exceptions import ResourceNotFoundError

class SystemConfigService(BaseService):
    def get_config(self, key: str) -> str:
        try:
            config = SystemConfig.objects.get(key=key)
            return config.value
        except SystemConfig.DoesNotExist:
            raise ResourceNotFoundError(f"Không tìm thấy cấu hình với key: {key}")

class NotificationService(BaseService):
    def send_notification(self, user_id: int, template_id: int) -> UserNotification:
        try:
            template = NotificationTemplate.objects.get(id=template_id)
        except NotificationTemplate.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy mẫu thông báo.")
            
        notification = UserNotification(
            user_id=user_id,
            template=template,
            is_read=False
        )
        notification.save()
        return notification
