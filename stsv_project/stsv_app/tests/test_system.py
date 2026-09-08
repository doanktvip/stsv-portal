from rest_framework import status
from django.urls import reverse
from .base import BaseAPITestCase
from stsv_app.models import SystemConfig, UserNotification, NotificationTemplate

class SystemConfigAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.config = SystemConfig.objects.create(
            key="MAX_STUDENTS_PER_CLASS",
            value="50",
            description="Số sinh viên tối đa một lớp",
            updated_by=self.admin
        )

    def test_student_get_configs(self):
        url = reverse('stsv_app:system-config-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_create_config_forbidden(self):
        url = reverse('stsv_app:system-config-list')
        self.client.force_authenticate(user=self.student)
        data = {"key": "NEW_KEY", "value": "123"}
        response = self.client.post(url, data)
        # Yêu cầu IsAdminRole nên sinh viên sẽ bị chặn
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_config(self):
        url = reverse('stsv_app:system-config-list')
        self.client.force_authenticate(user=self.admin)
        data = {"key": "SEMESTER_ACTIVE", "value": "2026_HK1"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_update_config(self):
        url = reverse('stsv_app:system-config-detail', kwargs={'pk': self.config.pk})
        self.client.force_authenticate(user=self.admin)
        data = {"value": "60"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.config.refresh_from_db()
        self.assertEqual(self.config.value, "60")


class UserNotificationAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        template1 = NotificationTemplate.objects.create(
            sender=self.admin,
            title="Đóng học phí",
            message="Vui lòng đóng học phí"
        )
        template2 = NotificationTemplate.objects.create(
            sender=self.admin,
            title="Cập nhật điểm",
            message="Đã có điểm"
        )
        self.noti1 = UserNotification.objects.create(
            user=self.student,
            template=template1,
            is_read=False
        )
        self.noti2 = UserNotification.objects.create(
            user=self.student,
            template=template2,
            is_read=False
        )

    def test_student_get_notifications(self):
        url = reverse('stsv_app:notification-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data_list = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(data_list), 2)

    def test_read_single_notification(self):
        url = reverse('stsv_app:notification-read', kwargs={'pk': self.noti1.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.noti1.refresh_from_db()
        self.assertTrue(self.noti1.is_read)
        self.assertFalse(self.noti2.is_read)

    def test_read_all_notifications(self):
        url = reverse('stsv_app:notification-read-all')
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.noti1.refresh_from_db()
        self.noti2.refresh_from_db()
        self.assertTrue(self.noti1.is_read)
        self.assertTrue(self.noti2.is_read)
