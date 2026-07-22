from .base import BaseService
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile
from .exceptions import ResourceNotFoundError, ValidationError, PermissionDeniedError
from django.contrib.auth.hashers import make_password

class UserService(BaseService):
    @BaseService.run_in_transaction
    def create_user(self, username, password, email, role=User.Role.STUDENT) -> User:
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username đã tồn tại.")
        user = User(username=username, email=email, role=role)
        user.password = make_password(password)
        user.save()
        return user

class StudentProfileService(BaseService):
    def get_profile(self, user_id: int) -> StudentProfile:
        try:
            return StudentProfile.objects.get(user_id=user_id)
        except StudentProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy hồ sơ sinh viên.")

    @BaseService.run_in_transaction
    def create_or_update_profile(self, user_id: int, data: dict) -> StudentProfile:
        profile, created = StudentProfile.objects.update_or_create(
            user_id=user_id, defaults=data
        )
        return profile

class OrgProfileService(BaseService):
    def update_status(self, org_id: int, status: str):
        try:
            org = OrgProfile.objects.get(id=org_id)
            org.status = status
            org.save()
            return org
        except OrgProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy tổ chức.")
