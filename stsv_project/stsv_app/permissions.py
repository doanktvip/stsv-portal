from rest_framework.permissions import IsAuthenticated
from stsv_app.models.users import User


class BaseRolePermission(IsAuthenticated):
    required_role = None

    def has_permission(self, request, view):
        has_base = super().has_permission(request, view)
        if not has_base:
            return False
        if request.user.role == "ADMIN":
            return True
        return request.user.role == self.required_role


class IsAdminRole(BaseRolePermission):
    required_role = User.Role.ADMIN


class IsStudentRole(BaseRolePermission):
    required_role = User.Role.STUDENT



class IsOrgOfficerRole(BaseRolePermission):
    required_role = User.Role.ORGOFFICER


class IsStudentOrBanCanSuRole(IsAuthenticated):
    def has_permission(self, request, view):
        has_base = super().has_permission(request, view)
        if not has_base:
            return False
        if request.user.role == "ADMIN":
            return True
        return request.user.role in [User.Role.STUDENT, User.Role.BANCANSU]

class IsClassPresident(IsAuthenticated):
    def has_permission(self, request, view):
        has_base = super().has_permission(request, view)
        if not has_base:
            return False
        if request.user.role == "ADMIN":
            return True
        if request.user.role == User.Role.BANCANSU:
            return hasattr(request.user, 'student_profile') and request.user.student_profile.presided_classes.exists()
        return False
