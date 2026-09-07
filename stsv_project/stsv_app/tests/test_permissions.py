from .base import BaseAPITestCase
from rest_framework.test import APIRequestFactory
from stsv_app.permissions import (
    BaseRolePermission, IsStudentRole,
    IsStudentOrBanCanSuRole, IsClassPresident
)
from django.contrib.auth.models import AnonymousUser

class PermissionsTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    def test_anonymous_permissions(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        perm = BaseRolePermission()
        self.assertFalse(perm.has_permission(request, None))
        
        perm_bcs = IsStudentOrBanCanSuRole()
        self.assertFalse(perm_bcs.has_permission(request, None))

        perm_cp = IsClassPresident()
        self.assertFalse(perm_cp.has_permission(request, None))


    def test_admin_bypass_permissions(self):
        request = self.factory.get('/')
        request.user = self.admin
        
        self.assertTrue(IsStudentRole().has_permission(request, None))
        self.assertTrue(IsStudentOrBanCanSuRole().has_permission(request, None))
        self.assertTrue(IsClassPresident().has_permission(request, None))

    def test_class_president_permission_false(self):
        request = self.factory.get('/')
        request.user = self.student
        self.assertFalse(IsClassPresident().has_permission(request, None))

