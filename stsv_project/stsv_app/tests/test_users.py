from rest_framework import status
from django.urls import reverse
from .base import BaseAPITestCase

class UserAccountAPITestCase(BaseAPITestCase):
    def test_get_me_as_student(self):
        url = reverse('stsv_app:user-me')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('student_id', response.data)

    def test_get_me_as_org_officer(self):
        url = reverse('stsv_app:user-me')
        self.client.force_authenticate(user=self.org_officer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('org_name', response.data)

    def test_get_me_as_admin(self):
        url = reverse('stsv_app:user-me')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)


    def test_change_password_success(self):
        url = reverse('stsv_app:user-change-password')
        self.student.set_password("123456")
        self.student.save()
        self.client.force_authenticate(user=self.student)
        data = {
            "old_password": "123456",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Đổi lại mk để không ảnh hưởng test khác
        self.student.set_password("123456")
        self.student.save()

    def test_change_password_wrong_old(self):
        url = reverse('stsv_app:user-change-password')
        self.student.set_password("123456")
        self.student.save()
        self.client.force_authenticate(user=self.student)
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_toggle_status_student(self):
        url = reverse('stsv_app:admin-account-toggle-status', kwargs={'pk': self.student.pk})
        self.client.force_authenticate(user=self.admin)
        
        # Khóa
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        
        # Mở khóa
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_admin_toggle_status_self(self):
        url = reverse('stsv_app:admin-account-toggle-status', kwargs={'pk': self.admin.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
