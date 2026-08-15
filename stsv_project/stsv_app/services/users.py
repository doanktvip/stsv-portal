from .base import BaseService
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile
from .exceptions import ResourceNotFoundError, ValidationError


class StudentProfileService(BaseService):
    def get_profile(self, user_or_id: User | int) -> StudentProfile:
        lookup = (
            {"user": user_or_id}
            if isinstance(user_or_id, User)
            else {"user_id": user_or_id}
        )
        try:
            return StudentProfile.objects.select_related(
                "faculty", "major", "cohort", "user"
            ).get(**lookup)
        except StudentProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy hồ sơ sinh viên.")


class LecturerProfileService(BaseService):
    def get_profile(self, user_or_id: User | int) -> LecturerProfile:
        lookup = (
            {"user": user_or_id}
            if isinstance(user_or_id, User)
            else {"user_id": user_or_id}
        )
        try:
            return LecturerProfile.objects.select_related("faculty", "user").get(
                **lookup
            )
        except LecturerProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy hồ sơ giảng viên.")


class OrgProfileService(BaseService):
    def get_profile(self, user_or_id: User | int) -> OrgProfile:
        lookup = (
            {"user": user_or_id}
            if isinstance(user_or_id, User)
            else {"user_id": user_or_id}
        )
        try:
            return OrgProfile.objects.select_related(
                "faculty", "parent_org", "advisor", "user"
            ).get(**lookup)
        except OrgProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy hồ sơ cán bộ tổ chức.")


class UserService(BaseService):
    def __init__(self):
        self.student_service = StudentProfileService()
        self.lecturer_service = LecturerProfileService()
        self.org_service = OrgProfileService()

    def get_user_profile(self, user: User):
        if user.role == User.Role.STUDENT:
            return self.student_service.get_profile(user)
        elif user.role == User.Role.LECTURER:
            return self.lecturer_service.get_profile(user)
        elif user.role == User.Role.ORGOFFICER:
            return self.org_service.get_profile(user)

        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> None:        
        if not user.check_password(old_password):
            raise ValidationError("Mật khẩu hiện tại không chính xác.")
        
        if old_password == new_password:
            raise ValidationError("Mật khẩu mới phải khác mật khẩu hiện tại.")
            
        user.set_password(new_password)
        user.save()
