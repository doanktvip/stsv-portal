from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from stsv_app.models.system import SystemConfig, UserNotification
from stsv_app.serializers.system import SystemConfigSerializer, UserNotificationSerializer

from stsv_app.permissions import IsAdminRole

class SystemConfigViewSet(viewsets.ModelViewSet):
    """
    API quản lý cấu hình hệ thống.
    Bất kỳ người dùng đã đăng nhập nào cũng có thể đọc cấu hình.
    Admin có quyền Thêm/Sửa/Xóa.
    Có thể lọc theo key: /system-configs/?key=SEMESTERS_PER_YEAR
    """
    queryset = SystemConfig.objects.all().order_by('key')
    serializer_class = SystemConfigSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["key"]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class UserNotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API quản lý thông báo của người dùng.
    """
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return UserNotification.objects.none()
        return UserNotification.objects.filter(user=user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({"detail": "Đã đánh dấu đọc."})
        
    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"detail": "Đã đánh dấu đọc tất cả."})
