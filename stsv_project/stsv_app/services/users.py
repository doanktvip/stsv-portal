from .base import BaseService
from .exceptions import ResourceNotFoundError, ValidationError
from stsv_app.models import User, StudentProfile, OrgProfile

class StudentProfileService(BaseService):
    def get_profile(self, user_or_id: User | int) -> StudentProfile:
        lookup = (
            {"user": user_or_id}
            if isinstance(user_or_id, User)
            else {"user_id": user_or_id}
        )
        try:
            return StudentProfile.objects.select_related(
                "faculty", "homeroom_class", "user"
            ).get(**lookup)
        except StudentProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy hồ sơ sinh viên.")


class OrgProfileService(BaseService):
    def get_profile(self, user_or_id: User | int) -> OrgProfile:
        lookup = (
            {"user": user_or_id}
            if isinstance(user_or_id, User)
            else {"user_id": user_or_id}
        )
        try:
            return OrgProfile.objects.select_related(
                "faculty", "parent_org", "user"
            ).get(**lookup)
        except OrgProfile.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy hồ sơ cán bộ tổ chức.")


class UserService(BaseService):
    def __init__(self):
        self.student_service = StudentProfileService()

        self.org_service = OrgProfileService()

    def get_user_profile(self, user: User):
        if user.role == User.Role.STUDENT:
            return self.student_service.get_profile(user)

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

    def toggle_account_status(self, target_user: User, requester: User) -> dict:
        if target_user == requester:
            raise ValidationError("Không thể tự khóa tài khoản của mình.")

        target_user.is_active = not target_user.is_active
        target_user.save(update_fields=["is_active"])

        action_msg = "Mở khóa" if target_user.is_active else "Khóa"
        return {
            "is_active": target_user.is_active,
            "message": f"{action_msg} tài khoản thành công.",
        }

