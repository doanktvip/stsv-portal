from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from stsv_app.models import SystemConfig, UserNotification
from stsv_app.serializers import SystemConfigSerializer, UserNotificationSerializer
from stsv_app.permissions import IsAdminRole
from stsv_app.services import SystemConfigService, NotificationService


class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all().order_by('key')
    serializer_class = SystemConfigSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["key"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_service = SystemConfigService()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def perform_create(self, serializer):
        config = self.config_service.create_config(
            validated_data=serializer.validated_data,
            updated_by=self.request.user,
        )
        serializer.instance = config

    def perform_update(self, serializer):
        config = self.config_service.update_config(
            instance=serializer.instance,
            validated_data=serializer.validated_data,
            updated_by=self.request.user,
        )
        serializer.instance = config


class UserNotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notification_service = NotificationService()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return UserNotification.objects.none()  # pragma: no cover
        return UserNotification.objects.filter(user=user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notification = self.get_object()
        self.notification_service.mark_as_read(notification)
        return Response({"detail": "Đã đánh dấu đọc."})

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        self.notification_service.mark_all_as_read(request.user)
        return Response({"detail": "Đã đánh dấu đọc tất cả."})
