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
        CLASS_APPROVED = "CLASS_APPROVED", "Lớp đã duyệt"
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
    criterion_1_score = models.IntegerField(default=0)
    criterion_2_score = models.IntegerField(default=0)
    criterion_3_score = models.IntegerField(default=0)
    criterion_4_score = models.IntegerField(default=0)
    criterion_5_score = models.IntegerField(default=0)


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
