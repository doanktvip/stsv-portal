from django.urls import reverse
from .base import BaseAPITestCase

class SemesterAPITestCase(BaseAPITestCase):
    def test_get_semesters_as_student(self):
        url = reverse('stsv_app:semester-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertIn('results', response.data)

    def test_semester_str(self):
        from stsv_app.models import Semester
        semester = Semester.objects.first()
        if semester:
            self.assertEqual(str(semester), semester.code)
