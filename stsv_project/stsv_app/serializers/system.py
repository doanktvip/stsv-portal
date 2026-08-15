from rest_framework import serializers
from stsv_app.models.system import SystemConfig

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['key', 'value', 'description']
