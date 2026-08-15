from rest_framework import viewsets, mixins, permissions
from django_filters.rest_framework import DjangoFilterBackend
from stsv_app.models.system import SystemConfig
from stsv_app.serializers.system import SystemConfigSerializer

class SystemConfigViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API lấy cấu hình hệ thống.
    Bất kỳ người dùng đã đăng nhập nào cũng có thể đọc cấu hình.
    Có thể lọc theo key: /system-configs/?key=SEMESTERS_PER_YEAR
    """
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["key"]
