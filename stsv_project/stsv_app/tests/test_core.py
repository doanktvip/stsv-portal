from rest_framework import status
from django.urls import reverse
from stsv_app.tests.base import BaseAPITestCase

class FacultyAPITestCase(BaseAPITestCase):
    def test_get_faculties_list(self):
        """
        Kiểm tra luồng lấy danh sách Khoa
        API này AllowAny nên không cần đăng nhập
        """
        url = reverse('stsv_app:faculty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Bọc trong pagination nên sẽ có 'results'
        self.assertIn('results', response.data)

class MajorAPITestCase(BaseAPITestCase):
    def test_get_majors_list(self):
        """
        Kiểm tra luồng lấy danh sách Chuyên ngành
        """
        url = reverse('stsv_app:major-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

class CohortAPITestCase(BaseAPITestCase):
    def test_get_cohorts_list(self):
        """
        Kiểm tra luồng lấy danh sách Khóa học (Cohort)
        """
        url = reverse('stsv_app:cohort-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
