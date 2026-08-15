from rest_framework.permissions import IsAuthenticated
from stsv_app.models.users import User


class BaseRolePermission(IsAuthenticated):
    required_role = None

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False

        return request.user.role == self.required_role


class IsAdminRole(BaseRolePermission):
    required_role = User.Role.ADMIN


class IsStudentRole(BaseRolePermission):
    required_role = User.Role.STUDENT


class IsLecturerRole(BaseRolePermission):
    required_role = User.Role.LECTURER


class IsOrgOfficerRole(BaseRolePermission):
    required_role = User.Role.ORGOFFICER
