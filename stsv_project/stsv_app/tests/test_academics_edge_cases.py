from django.test import TestCase
from stsv_app.models.users import User
from stsv_app.services.academics import (
    SubjectService,
    CourseClassService,
    StudentCourseService,
    ScheduleService,
    StudentSemesterSummaryService
)

class AcademicsServiceEdgeCasesTestCase(TestCase):
    def setUp(self):
        # Tạo users nhưng cố tình không tạo Profile (StudentProfile, LecturerProfile)
        self.student_no_profile = User.objects.create(username="s_no_prof", role=User.Role.STUDENT)
        self.lecturer_no_profile = User.objects.create(username="l_no_prof", role=User.Role.LECTURER)
        self.other_user = User.objects.create(username="other", role=User.Role.ORGOFFICER)

    def test_get_subjects_for_user_no_profile(self):
        service = SubjectService()
        qs = service.get_subjects_for_user(self.lecturer_no_profile)
        self.assertFalse(qs.exists())

    def test_get_course_classes_no_profile(self):
        service = CourseClassService()
        
        # Lecturer no profile
        qs_l = service.get_course_classes(self.lecturer_no_profile)
        self.assertFalse(qs_l.exists())
        
        # Student no profile
        qs_s = service.get_course_classes(self.student_no_profile)
        self.assertFalse(qs_s.exists())
        
        # Other role
        qs_o = service.get_course_classes(self.other_user)
        self.assertFalse(qs_o.exists())

    def test_get_my_courses_no_profile(self):
        service = StudentCourseService()
        qs = service.get_my_courses(self.student_no_profile)
        self.assertFalse(qs.exists())

    def test_get_personal_schedules_no_profile(self):
        service = ScheduleService()
        # Student no profile
        qs_s = service.get_personal_schedules(self.student_no_profile)
        self.assertFalse(qs_s.exists())
        
        # Lecturer no profile
        qs_l = service.get_personal_schedules(self.lecturer_no_profile)
        self.assertFalse(qs_l.exists())
        
        # Other role
        qs_o = service.get_personal_schedules(self.other_user)
        self.assertFalse(qs_o.exists())

    def test_get_my_summaries_no_profile(self):
        service = StudentSemesterSummaryService()
        qs = service.get_my_summaries(self.student_no_profile)
        self.assertFalse(qs.exists())
