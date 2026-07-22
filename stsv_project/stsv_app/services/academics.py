from .base import BaseService
from stsv_app.models.academics import StudentCourse, CourseClass, Semester, Schedule
from .exceptions import ResourceNotFoundError, ValidationError


class AcademicService(BaseService):
    def register_course(
        self, student_profile_id: int, course_class_id: int
    ) -> StudentCourse:
        """Đăng ký học phần cho sinh viên."""
        try:
            course = CourseClass.objects.get(id=course_class_id)
        except CourseClass.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy lớp học phần này.")

        if course.current_enrollment >= course.capacity:
            raise ValidationError("Lớp học phần đã đầy.")

        # Kiểm tra xem đã đăng ký chưa
        if StudentCourse.objects.filter(
            student_id=student_profile_id, course_class_id=course_class_id
        ).exists():
            raise ValidationError("Sinh viên đã đăng ký lớp học phần này rồi.")

        # Thực hiện đăng ký
        enrollment = StudentCourse(
            student_id=student_profile_id, course_class_id=course_class_id
        )
        enrollment.save()

        # Cập nhật số lượng
        course.current_enrollment += 1
        course.save()

        return enrollment


class ScheduleService(BaseService):
    def get_student_schedule(self, student_profile_id: int, semester_id: int):
        """Lấy thời khóa biểu của sinh viên trong một kỳ học cụ thể."""
        course_classes = StudentCourse.objects.filter(
            student_id=student_profile_id, course_class__semester_id=semester_id
        ).values_list("course_class", flat=True)

        schedules = Schedule.objects.filter(course_class_id__in=course_classes)
        return schedules
