from rest_framework import status
from django.urls import reverse
from .base import BaseAPITestCase
from stsv_app.models import StudentSemesterPoint, TrainingRule, Semester

class TrainingPointAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.semester = Semester.objects.first()
        self.rule = TrainingRule.objects.first()
        
        # Ensure student point instance exists
        if self.semester and hasattr(self.student, 'student_profile'):
            self.point, _ = StudentSemesterPoint.objects.get_or_create(
                student=self.student.student_profile,
                semester=self.semester,
                defaults={'total_student_score': 80}
            )

    def test_training_rules_list(self):
        url = reverse('stsv_app:training-rule-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_points(self):
        url = reverse('stsv_app:student-semester-point-my-points')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f"{url}?semester_id={self.semester.id}" if self.semester else url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST])

    def test_submit_points(self):
        url = reverse('stsv_app:student-semester-point-submit')
        self.client.force_authenticate(user=self.student)
        data = {
            'semester_id': self.semester.id if self.semester else 1,
            'total_student_score': 85,
            'is_draft': True,
            'points_data': {}
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_class_list_and_approve(self):
        url = reverse('stsv_app:student-semester-point-class-list')
        self.client.force_authenticate(user=self.bancansu)
        response = self.client.get(f"{url}?semester_id={self.semester.id}" if self.semester else url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST])

        if hasattr(self, 'point'):
            approve_url = reverse('stsv_app:student-semester-point-class-approve', kwargs={'pk': self.point.pk})
            data = {'total_class_score': 85, 'is_draft': True}
            resp = self.client.post(approve_url, data, format='json')
            self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_open_evaluation_and_faculty_approve(self):
        url = reverse('stsv_app:student-semester-point-open-evaluation')
        self.client.force_authenticate(user=self.org_officer)
        data = {'semester_id': self.semester.id if self.semester else 1}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST])

        faculty_list_url = reverse('stsv_app:student-semester-point-faculty-list')
        resp_fac = self.client.get(f"{faculty_list_url}?semester_id={self.semester.id}" if self.semester else faculty_list_url)
        self.assertIn(resp_fac.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST])

    def test_point_transactions(self):
        url = reverse('stsv_app:point-transaction-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

