from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from stsv_app.models import StudentProfile, OrgProfile
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("Tài khoản hoặc mật khẩu không chính xác.")
    }


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    default_error_messages = {
        "bad_tok": _("Mã xác thực (Token) không hợp lệ hoặc đã hết hạn.")
    }

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except (InvalidToken, TokenError):
            raise exceptions.AuthenticationFailed(
                _("Mã xác thực (Token) không hợp lệ hoặc đã hết hạn.")
            )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "first_name", "last_name", "is_active"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    faculty_name = serializers.CharField(
        source="faculty.name", read_only=True, default=None
    )
    class_name = serializers.CharField(
        source="homeroom_class.name", read_only=True, default=None
    )

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "student_id",
            "full_name",
            "class_name",
            "faculty_name",
            "cohort_year",
        ]
        read_only_fields = ["student_id"]


class OrgProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    faculty_name = serializers.CharField(
        source="faculty.name", read_only=True, default=None
    )
    parent_org_name = serializers.CharField(
        source="parent_org.org_name", read_only=True, default=None
    )
    class Meta:
        model = OrgProfile
        fields = [
            "id",
            "user",
            "org_name",
            "org_type",
            "faculty",
            "faculty_name",
            "parent_org",
            "parent_org_name",
            "description",
            "established_date",
            "status",
        ]
        read_only_fields = ["status"]
