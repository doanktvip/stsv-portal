from django.db import models


class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey("stsv_app.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.key


class NotificationTemplate(models.Model):
    class Type(models.TextChoices):
        REMINDER = "REMINDER", "Nhắc nhở"
        ALERT = "ALERT", "Cảnh báo"
        GENERAL = "GENERAL", "Thông báo chung"
        EVENT = "EVENT", "Sự kiện"

    sender = models.ForeignKey(
        "stsv_app.User", on_delete=models.CASCADE, related_name="sent_notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.GENERAL)
    related_link = models.CharField(max_length=255, blank=True, null=True)
    action_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserNotification(models.Model):
    user = models.ForeignKey(
        "stsv_app.User", on_delete=models.CASCADE, related_name="notifications"
    )
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
