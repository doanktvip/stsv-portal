from rest_framework import serializers
from stsv_app.models import SystemConfig, NotificationTemplate, UserNotification

class SystemConfigSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'description', 'updated_by_name']

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ['title', 'message', 'type', 'related_link', 'action_data', 'created_at']

class UserNotificationSerializer(serializers.ModelSerializer):
    template = NotificationTemplateSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'template', 'is_read', 'created_at']
