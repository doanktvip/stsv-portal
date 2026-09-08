from stsv_app.models import SystemConfig, UserNotification, User
from .base import BaseService


class SystemConfigService(BaseService):
    def create_config(self, validated_data: dict, updated_by: User) -> SystemConfig:
        return SystemConfig.objects.create(**validated_data, updated_by=updated_by)

    def update_config(self, instance: SystemConfig, validated_data: dict, updated_by: User) -> SystemConfig:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = updated_by
        instance.save()
        return instance


class NotificationService(BaseService):
    def mark_as_read(self, notification: UserNotification) -> UserNotification:
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return notification

    def mark_all_as_read(self, user: User) -> int:
        updated_count = (
            UserNotification.objects
            .filter(user=user, is_read=False)
            .update(is_read=True)
        )
        return updated_count
