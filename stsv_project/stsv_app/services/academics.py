from django.utils import timezone
from .base import BaseService
from stsv_app.models.users import User
from stsv_app.models.academics import StudentCourse, CourseClass, Semester, Schedule, Subject, EducationProgram
from .exceptions import ResourceNotFoundError, ValidationError


class EducationProgramService(BaseService):
    def get_programs_for_student(self, student_profile):
        return EducationProgram.objects.filter(
            major=student_profile.major,
            cohort=student_profile.cohort
        )


class SubjectService(BaseService):
    def get_subjects_for_user(self, user: User):
        qs = Subject.objects.select_related("faculty").prefetch_related("prerequisite_subjects").all().order_by("id")

        if user.role == User.Role.LECTURER:
            if hasattr(user, 'lecturer_profile'):
                return qs.filter(faculty=user.lecturer_profile.faculty)
            return qs.none()

        return qs


class SemesterService(BaseService):
    def get_semesters_for_user(self, user):
        today = timezone.now().date()
        # Cho phép lấy cả học kỳ hiện tại và học kỳ sắp tới (trong vòng 60 ngày tới)
        future_date = today + timezone.timedelta(days=60)
        qs = Semester.objects.filter(start_date__lte=future_date)
        
        # Nếu là sinh viên, chỉ lấy các học kỳ từ năm nhập học trở đi
        if user.role == User.Role.STUDENT and hasattr(user, 'student_profile') and user.student_profile.cohort:
            enrollment_year = user.student_profile.cohort.enrollment_year
            qs = qs.filter(start_date__year__gte=enrollment_year)
            
        # Nếu là giảng viên, chỉ lấy các học kỳ mà giảng viên đó có lớp dạy
        elif user.role == User.Role.LECTURER and hasattr(user, 'lecturer_profile'):
            qs = qs.filter(courseclass__lecturer=user.lecturer_profile).distinct()
            
        # Sắp xếp giảm dần theo ngày bắt đầu (kỳ mới nhất lên đầu)
        return qs.order_by("-start_date")

class CourseClassService(BaseService):
    def get_course_classes(self, user):
        qs = CourseClass.objects.select_related("subject", "semester", "lecturer").all()

        if user.role == User.Role.ADMIN:
            return qs
            
        elif user.role == User.Role.LECTURER:
            if hasattr(user, 'lecturer_profile'):
                return qs.filter(subject__faculty=user.lecturer_profile.faculty)
            return qs.none()
            
        elif user.role == User.Role.STUDENT:
            if hasattr(user, 'student_profile'):
                return qs.filter(subject__faculty=user.student_profile.faculty)
            return qs.none()
            
        return qs.none()

class StudentCourseService(BaseService):
    def get_my_courses(self, user):
        if hasattr(user, 'student_profile'):
            return StudentCourse.objects.filter(student=user.student_profile).select_related(
                "course_class", 
                "course_class__subject", 
                "course_class__semester"
            )
        return StudentCourse.objects.none()

class ScheduleService(BaseService):
    def get_personal_schedules(self, user):
        if user.role == User.Role.STUDENT and hasattr(user, 'student_profile'):
            return Schedule.objects.filter(
                course_class__studentcourse__student=user.student_profile
            ).select_related("course_class", "course_class__subject", "course_class__semester")
        elif user.role == User.Role.LECTURER and hasattr(user, 'lecturer_profile'):
            return Schedule.objects.filter(
                course_class__lecturer=user.lecturer_profile
            ).select_related("course_class", "course_class__subject", "course_class__semester")
        return Schedule.objects.none()
