from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Lưu lịch sử đồng bộ dữ liệu từ hệ thống của trường (để biết lúc nào lấy điểm, lấy thời khóa biểu bị lỗi hay thành công).
class IntegrationSyncLog(models.Model):
    class SyncType(models.TextChoices):
        STUDENTS = "STUDENTS", "Sinh viên"
        SCORES = "SCORES", "Điểm số"
        SCHEDULES = "SCHEDULES", "Thời khóa biểu"
        FACULTIES = "FACULTIES", "Khoa/Ngành"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Thành công"
        PARTIAL_SUCCESS = "PARTIAL_SUCCESS", "Thành công một phần"
        FAILED = "FAILED", "Thất bại"

    sync_type = models.CharField(max_length=50, choices=SyncType.choices)
    status = models.CharField(max_length=20, choices=Status.choices)
    error_details = models.JSONField(blank=True, null=True)
    synced_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        "stsv_app.User", on_delete=models.SET_NULL, null=True, blank=True
    )


# Cấu hình quy tắc đổi điểm từ thang 10 sang thang 4 và điểm chữ (A, B, C, D, F).
class GradeConversionRule(models.Model):
    class Classification(models.TextChoices):
        PASS = "PASS", "Đạt"
        FAIL = "FAIL", "Không đạt"

    min_score_10 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    max_score_10 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    letter_grade = models.CharField(max_length=5)
    score_4 = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
    )
    classification = models.CharField(max_length=20, choices=Classification.choices)
    updated_by = models.ForeignKey(
        "stsv_app.User", on_delete=models.SET_NULL, null=True, blank=True
    )


# Thông tin môn học (số tín chỉ, môn tiên quyết).
class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    credits = models.IntegerField(validators=[MinValueValidator(0)])
    faculty = models.ForeignKey("stsv_app.Faculty", on_delete=models.CASCADE)
    prerequisite_subjects = models.ManyToManyField(
        "self", blank=True, symmetrical=False
    )

    def __str__(self):
        return self.name


# Chương trình đào tạo. Quy định chuyên ngành nào, khóa nào phải học những môn gì, vào kỳ nào.
class EducationProgram(models.Model):
    major = models.ForeignKey("stsv_app.Major", on_delete=models.CASCADE)
    cohort = models.ForeignKey("stsv_app.Cohort", on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    recommended_semester = models.IntegerField()
    is_mandatory = models.BooleanField(default=True)


# Thông tin Học kỳ (Kỳ 1 năm 2023-2024, thời gian bắt đầu/kết thúc).
class Semester(models.Model):
    code = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.code


# Lớp học phần (Ví dụ: Lớp C++ sáng thứ 2).
class CourseClass(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(
        "stsv_app.LecturerProfile", on_delete=models.SET_NULL, null=True
    )
    class_code = models.CharField(max_length=50)
    capacity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    current_enrollment = models.IntegerField(
        default=0, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.subject.name} - {self.class_code}"


# Các thành phần điểm của 1 môn (Điểm danh 10%, Giữa kỳ 30%, Cuối kỳ 60%).
class ScoreComponent(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    weight_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.subject.name} - {self.name} ({self.weight_percentage}%)"


# Thông tin sinh viên đăng ký lớp học phần và điểm tổng kết môn học.
class StudentCourse(models.Model):
    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE)
    total_score_10 = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    total_score_4 = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    total_score_letter = models.CharField(max_length=5, null=True, blank=True)
    is_passed = models.BooleanField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.course_class.class_code}"


# Điểm chi tiết cho từng thành phần (sinh viên A được 8đ giữa kỳ).
class StudentScoreDetail(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE)
    score_component = models.ForeignKey(ScoreComponent, on_delete=models.CASCADE)
    score_value = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    is_deleted = models.BooleanField(default=False, db_index=True)


# Tổng kết GPA, tín chỉ, điểm rèn luyện của sinh viên sau mỗi học kỳ.
class StudentSemesterSummary(models.Model):
    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    semester_gpa_4 = models.DecimalField(max_digits=3, decimal_places=2)
    semester_earned_credits = models.IntegerField()
    semester_training_points = models.IntegerField()
    training_point_classification = models.CharField(max_length=50)
    cumulative_gpa_4 = models.DecimalField(max_digits=3, decimal_places=2)
    cumulative_earned_credits = models.IntegerField()
    cumulative_training_points = models.IntegerField()


# Thời khóa biểu, lịch học và lịch thi của từng lớp học phần.
class Schedule(models.Model):
    class Type(models.TextChoices):
        CLASS = "CLASS", "Học trên lớp"
        EXAM = "EXAM", "Lịch thi"

    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.CLASS)
    day_of_week = models.IntegerField()
    exact_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    is_makeup_class = models.BooleanField(default=False)
    sync_id = models.CharField(max_length=255, null=True, blank=True)
