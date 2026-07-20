from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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


class EducationProgram(models.Model):
    major = models.ForeignKey("stsv_app.Major", on_delete=models.CASCADE)
    cohort = models.ForeignKey("stsv_app.Cohort", on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    recommended_semester = models.IntegerField()
    is_mandatory = models.BooleanField(default=True)


class Semester(models.Model):
    code = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.code


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


class ScoreComponent(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    weight_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.subject.name} - {self.name} ({self.weight_percentage}%)"


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


class StudentScoreDetail(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE)
    score_component = models.ForeignKey(ScoreComponent, on_delete=models.CASCADE)
    score_value = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    is_deleted = models.BooleanField(default=False, db_index=True)


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
