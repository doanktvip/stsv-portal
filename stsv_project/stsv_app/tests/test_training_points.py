from django.urls import reverse
from rest_framework import status
from stsv_app.tests.base import BaseAPITestCase
from stsv_app.models.training_points import TrainingCriterion, StudentSemesterPoint, SemesterPointDetail
from stsv_app.models.academics import Semester

class TrainingPointAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Tạo Criterion mẫu
        self.criterion = TrainingCriterion.objects.create(
            code="TC01",
            name="Tham gia hoạt động Đoàn",
            max_points=10
        )
        
        self.semester = Semester.objects.first()

        # Tạo SemesterPoint và Detail để test hàm __str__
        self.student_point = StudentSemesterPoint.objects.create(
            student=self.student.student_profile,
            semester=self.semester,
            status=StudentSemesterPoint.Status.DRAFT
        )
        self.point_detail = SemesterPointDetail.objects.create(
            semester_point=self.student_point,
            criterion=self.criterion,
            student_score=5
        )

    def test_get_training_criteria(self):
        """Test API lấy danh sách các tiêu chí điểm rèn luyện"""
        url = reverse('stsv_app:training-criterion-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_models_str_methods(self):
        """Test các hàm __str__ của models để đảm bảo 100% coverage cho file models"""
        self.assertEqual(str(self.criterion), "Tham gia hoạt động Đoàn")
        self.assertIn("TC01", str(self.point_detail))
        self.assertIn(str(self.student.student_profile.student_id), str(self.point_detail))
