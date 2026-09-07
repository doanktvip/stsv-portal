from django.db import models
from cloudinary.models import CloudinaryField


class TrainingCriterion(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Ví dụ: Điều 1, Điều 2")
    max_points = models.IntegerField(default=20, help_text="Trần điểm tối đa cho Điều này")
    
    def __str__(self):
        return self.name

class TrainingRuleGroup(models.Model):
    criterion = models.ForeignKey(TrainingCriterion, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    is_single_choice = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {'Single' if self.is_single_choice else 'Multiple'}"

class TrainingRule(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="Mã quy tắc, ví dụ: 199")
    description = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    criterion = models.ForeignKey(TrainingCriterion, on_delete=models.CASCADE, related_name="rules")
    group = models.ForeignKey(TrainingRuleGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='rules')
    is_proof_required = models.BooleanField(default=False)
    is_event_rule = models.BooleanField(default=False, help_text="Là quy tắc để lưu điểm cộng tự động từ sự kiện")

    def __str__(self):
        return f"{self.code} - {self.description}"

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
    
    # Lưu tổng điểm đã phân rã theo từng Điều, cấu trúc JSON: {"categories": [...]}
    points_data = models.JSONField(default=dict, blank=True)
    class_points_data = models.JSONField(default=dict, blank=True)
    faculty_points_data = models.JSONField(default=dict, blank=True)
    
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
        "stsv_app.OrgProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_approved_training_points",
    )
    faculty_approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.student.student_id} - {self.semester.code} - {self.total_final_score}đ"


# Bảng gộp chung để lưu Lịch sử cộng/trừ điểm và Minh chứng sinh viên nộp.
class PointTransaction(models.Model):
    class Status(models.TextChoices):
        AUTO_APPROVED = "AUTO_APPROVED", "Hệ thống tự duyệt"
        PENDING = "PENDING", "Chờ duyệt minh chứng"
        APPROVED = "APPROVED", "Đã duyệt minh chứng"
        REJECTED = "REJECTED", "Từ chối"

    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    semester = models.ForeignKey("stsv_app.Semester", on_delete=models.CASCADE)
    
    # Quy tắc cộng điểm
    rule = models.ForeignKey("stsv_app.TrainingRule", on_delete=models.SET_NULL, null=True, blank=True) 
    
    # Sự kiện liên quan nếu là điểm tự động từ việc tham gia sự kiện.
    event = models.ForeignKey(
        "stsv_app.Event", on_delete=models.SET_NULL, null=True, blank=True
    )
    
    points_changed = models.IntegerField()
    reason = models.CharField(max_length=255)
    
    # Ảnh minh chứng nếu sinh viên tự nộp
    proof_image = CloudinaryField("Minh chứng", folder="point_proofs", blank=True, null=True)
    
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AUTO_APPROVED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.rule.code if self.rule else 'Event'}: {self.points_changed}đ"
