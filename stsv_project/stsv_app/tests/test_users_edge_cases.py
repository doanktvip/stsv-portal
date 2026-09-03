from django.test import TestCase
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile
from stsv_app.services.users import (
    StudentProfileService,
    LecturerProfileService,
    OrgProfileService,
    UserService
)
from stsv_app.services.exceptions import ResourceNotFoundError, ValidationError

class UserServiceEdgeCasesTestCase(TestCase):
    def setUp(self):
        self.student_user = User.objects.create(username="student1", role=User.Role.STUDENT)
        self.student_user.set_password("oldpassword")
        self.student_user.save()

        self.lecturer_user = User.objects.create(username="lecturer1", role=User.Role.LECTURER)
        
        self.org_user = User.objects.create(username="org1", role=User.Role.ORGOFFICER)
        self.org_profile = OrgProfile.objects.create(user=self.org_user, org_name="Org1", org_type=OrgProfile.OrgType.CLUB)

        self.admin_user = User.objects.create(username="admin1", role=User.Role.ADMIN)

        self.user_service = UserService()

    def test_student_profile_not_found(self):
        service = StudentProfileService()
        with self.assertRaises(ResourceNotFoundError):
            service.get_profile(self.student_user)
            
    def test_lecturer_profile_not_found(self):
        service = LecturerProfileService()
        with self.assertRaises(ResourceNotFoundError):
            service.get_profile(self.lecturer_user)

    def test_org_profile_service_success(self):
        service = OrgProfileService()
        profile = service.get_profile(self.org_user)
        self.assertEqual(profile, self.org_profile)
        
    def test_org_profile_service_not_found(self):
        # Tạo org_user2 nhưng không tạo OrgProfile
        org_user2 = User.objects.create(username="org2", role=User.Role.ORGOFFICER)
        service = OrgProfileService()
        with self.assertRaises(ResourceNotFoundError):
            service.get_profile(org_user2)

    def test_get_user_profile_org(self):
        profile = self.user_service.get_user_profile(self.org_user)
        self.assertEqual(profile, self.org_profile)
        
    def test_get_user_profile_admin(self):
        profile = self.user_service.get_user_profile(self.admin_user)
        # Vì admin không có profile riêng, trả về chính user
        self.assertEqual(profile, self.admin_user)

    def test_change_password_same_password(self):
        with self.assertRaises(ValidationError) as ctx:
            self.user_service.change_password(self.student_user, "oldpassword", "oldpassword")
        self.assertEqual(str(ctx.exception), "Mật khẩu mới phải khác mật khẩu hiện tại.")
