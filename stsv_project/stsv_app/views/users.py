from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions, mixins, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from stsv_app.serializers.users import (
    UserSerializer, StudentProfile, LecturerProfile, OrgProfile,
    StudentProfileSerializer,
    LecturerProfileSerializer,
    OrgProfileSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    ChangePasswordSerializer,
    UserDeviceSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from stsv_app.services import UserService
from stsv_app.models.users import UserDevice, User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    @action(methods=["get"], url_path="me", detail=False)
    def me(self, request):
        profile_or_user = self.user_service.get_user_profile(request.user)

        if isinstance(profile_or_user, StudentProfile):
            serializer = StudentProfileSerializer(profile_or_user)
        elif isinstance(profile_or_user, LecturerProfile):
            serializer = LecturerProfileSerializer(profile_or_user)
        elif isinstance(profile_or_user, OrgProfile):
            serializer = OrgProfileSerializer(profile_or_user)
        else:
            serializer = UserSerializer(profile_or_user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["post"], url_path="change-password", detail=False)
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        self.user_service.change_password(
            request.user, 
            serializer.validated_data['old_password'], 
            serializer.validated_data['new_password']
        )
        
        return Response({"message": "Đổi mật khẩu thành công."})
        
    @action(methods=["post"], url_path="devices", detail=False)
    def register_device(self, request):

        serializer = UserDeviceSerializer(data=request.data)
        if serializer.is_valid():
            UserDevice.objects.update_or_create(
                user=request.user,
                device_os=serializer.validated_data.get("device_os"),
                defaults={
                    "fcm_token": serializer.validated_data.get("fcm_token")
                }
            )
            return Response({"message": "Đăng ký thiết bị thành công."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LecturerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = LecturerProfile.objects.select_related("user", "faculty").all().order_by("id")
    serializer_class = LecturerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["faculty", "department"]
    search_fields = ["lecturer_id", "full_name"]
    ordering_fields = ["id", "lecturer_id", "full_name"]


class OrgViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        OrgProfile.objects.select_related("user", "faculty", "parent_org", "advisor")
        .all()
        .order_by("id")
    )
    serializer_class = OrgProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["org_type", "status", "faculty"]
    search_fields = ["org_name"]
    ordering_fields = ["id", "org_name", "established_date"]

class AdminAccountViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "date_joined"]

    @action(methods=["post"], detail=True, url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"message": "Không thể tự khóa tài khoản của mình."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = not user.is_active
        user.save()
        status_msg = "Mở khóa" if user.is_active else "Khóa"
        return Response({
            "status": "success",
            "message": f"{status_msg} tài khoản thành công.", 
            "is_active": user.is_active
        })
