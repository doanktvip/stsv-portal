from django.utils import timezone
from stsv_app.models.system import SystemConfig, NotificationTemplate, UserNotification
from stsv_app.models.users import User

def seed_system():
    print("--- Seeding System Data ---")
    now = timezone.now()
    user = User.objects.first()
    if not user:
        return
        
    SystemConfig.objects.get_or_create(key="maintenance_mode", defaults={"value": "false", "description": "Bật tắt bảo trì", "updated_by": user})
    
    tmpl, _ = NotificationTemplate.objects.get_or_create(
        title="Test thông báo",
        defaults={
            "sender": user,
            "message": "Đây là thông báo test",
            "type": NotificationTemplate.Type.GENERAL
        }
    )

    UserNotification.objects.get_or_create(
        user=user,
        template=tmpl,
        defaults={
            "is_read": False,
        }
    )

    print("System data seeded successfully.")
