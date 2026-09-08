from rest_framework import status
from django.urls import reverse
from .base import BaseAPITestCase

class FacultyAPITestCase(BaseAPITestCase):
    def test_get_faculties_list(self):
        url = reverse('stsv_app:faculty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Bọc trong pagination nên sẽ có 'results'
        self.assertIn('results', response.data)

    def test_models_str(self):
        if hasattr(self.student, 'student_profile'):
            faculty = self.student.student_profile.faculty
            if faculty:
                self.assertTrue(len(str(faculty)) > 0)
            hc = self.student.student_profile.homeroom_class
            if hc:
                self.assertTrue(len(str(hc)) > 0)


