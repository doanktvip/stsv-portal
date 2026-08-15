from django.db import models


# Các tiêu chí cộng/trừ điểm rèn luyện (VD: Tham gia NCKH được cộng 5đ).
class TrainingCriterion(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    max_points = models.IntegerField()

    def __str__(self):
        return self.name


# Tổng điểm rèn luyện của sinh viên trong một học kỳ cụ thể.
class StudentSemesterPoint(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Nháp"
        SUBMITTED = "SUBMITTED", "Đã nộp"
        CLASS_APPROVED = "CLASS_APPROVED", "Lớp trưởng đã duyệt"
        FACULTY_APPROVED = "FACULTY_APPROVED", "Khoa đã duyệt"

    student = models.ForeignKey(
        "stsv_app.StudentProfile",
        on_delete=models.CASCADE,
        related_name="training_points",
    )
    semester = models.ForeignKey("stsv_app.Semester", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    total_student_score = models.IntegerField(default=0)
    total_class_score = models.IntegerField(default=0)
    total_final_score = models.IntegerField(default=0)
    class_approved_by = models.ForeignKey(
        "stsv_app.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_approved_training_points",
    )
    class_approved_at = models.DateTimeField(null=True, blank=True)
    faculty_approved_by = models.ForeignKey(
        "stsv_app.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_approved_training_points",
    )
    faculty_approved_at = models.DateTimeField(null=True, blank=True)


class SemesterPointDetail(models.Model):
    semester_point = models.ForeignKey(
        StudentSemesterPoint,
        on_delete=models.CASCADE,
        related_name="details",
    )
    criterion = models.ForeignKey(TrainingCriterion, on_delete=models.CASCADE)
    student_score = models.IntegerField(default=0)
    class_score = models.IntegerField(default=0)
    final_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.semester_point.student.student_id} - {self.criterion.code}"


# Minh chứng minh họa (hình ảnh, giấy khen) mà sinh viên tải lên để xin cộng điểm.
class PointProof(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ duyệt"
        APPROVED = "APPROVED", "Đã duyệt"
        REJECTED = "REJECTED", "Từ chối"

    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    semester = models.ForeignKey("stsv_app.Semester", on_delete=models.CASCADE)
    criterion = models.ForeignKey(TrainingCriterion, on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=255)
    file_url = models.FileField(upload_to="point_proofs/")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )


# Lịch sử các lần cộng/trừ điểm rèn luyện để dễ dàng đối soát.
class PointHistory(models.Model):
    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    semester = models.ForeignKey("stsv_app.Semester", on_delete=models.CASCADE)
    criterion = models.ForeignKey(TrainingCriterion, on_delete=models.CASCADE)
    event = models.ForeignKey(
        "stsv_app.Event", on_delete=models.SET_NULL, null=True, blank=True
    )
    points_changed = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
