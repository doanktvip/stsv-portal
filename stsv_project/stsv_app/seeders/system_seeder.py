import random
from django.utils import timezone
from stsv_app.models import SystemConfig, NotificationTemplate, UserNotification, User

def seed_system():
    print("--- Nạp Dữ Liệu Cấu Hình Hệ Thống & Thông Báo ---")
    now = timezone.now()
    user = User.objects.first()
    if not user:
        return
        
    SystemConfig.objects.get_or_create(key="maintenance_mode", defaults={"value": "false", "description": "Bật tắt bảo trì", "updated_by": user})
    
    templates_to_create = []
    for t_choice in NotificationTemplate.Type.choices:
        t_type = t_choice[0]
        tmpl, _ = NotificationTemplate.objects.get_or_create(
            title=f"Test thông báo {t_choice[1]}",
            defaults={
                "sender": user,
                "message": f"Đây là thông báo test loại {t_type}",
                "type": t_type
            }
        )
        templates_to_create.append(tmpl)

    notifications_to_create = []
    for tmpl in templates_to_create:
        if not UserNotification.objects.filter(user=user, template=tmpl).exists():
            notifications_to_create.append(UserNotification(
                user=user,
                template=tmpl,
                is_read=random.choice([True, False])
            ))
            
    if notifications_to_create:
        UserNotification.objects.bulk_create(notifications_to_create)

    print("Nạp dữ liệu hệ thống thành công.")

