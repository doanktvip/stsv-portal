from rest_framework import status
from django.urls import reverse
from stsv_app.tests.base import BaseAPITestCase

class StudentEducationProgramAPITestCase(BaseAPITestCase):
    def test_get_education_programs_success(self):
        url = reverse('stsv_app:education-program-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Có thể có phân trang hoặc list, ta chỉ cần gọi GET thành công là đã cover được logic

    def test_get_education_programs_unauthorized(self):
        url = reverse('stsv_app:education-program-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubjectAPITestCase(BaseAPITestCase):
    def test_lecturer_get_subjects(self):
        url = reverse('stsv_app:subject-list')
        self.client.force_authenticate(user=self.lecturer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_get_subjects_forbidden(self):
        url = reverse('stsv_app:subject-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        # API này yêu cầu IsAdminRole hoặc IsLecturerRole nên sinh viên sẽ bị cấm
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SemesterAPITestCase(BaseAPITestCase):
    def test_get_semesters_as_student(self):
        url = reverse('stsv_app:semester-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_semesters_as_lecturer(self):
        url = reverse('stsv_app:semester-list')
        self.client.force_authenticate(user=self.lecturer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CourseClassAPITestCase(BaseAPITestCase):
    def test_student_get_course_classes(self):
        url = reverse('stsv_app:course-class-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_lecturer_get_course_classes(self):
        url = reverse('stsv_app:course-class-list')
        self.client.force_authenticate(user=self.lecturer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_admin_get_course_classes(self):
        url = reverse('stsv_app:course-class-list')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StudentCourseAPITestCase(BaseAPITestCase):
    def test_student_get_my_courses(self):
        url = reverse('stsv_app:student-course-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ScheduleAPITestCase(BaseAPITestCase):
    def test_student_get_schedules(self):
        url = reverse('stsv_app:schedule-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_lecturer_get_schedules(self):
        url = reverse('stsv_app:schedule-list')
        self.client.force_authenticate(user=self.lecturer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_schedules_by_exact_date(self):
        url = reverse('stsv_app:schedule-list')
        self.client.force_authenticate(user=self.student)
        # Test truyền query parameter để chạy vào phần code filter
        response = self.client.get(url, {'exact_date': '2026-09-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StudentSemesterSummaryAPITestCase(BaseAPITestCase):
    def test_get_semester_summaries(self):
        url = reverse('stsv_app:semester-summary-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
