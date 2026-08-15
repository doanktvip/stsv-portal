from django.db import models
from cloudinary.models import CloudinaryField



# Báo cáo hỏng hóc cơ sở vật chất (hỏng quạt, hỏng máy chiếu phòng học).
class FacilityReport(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Thấp"
        MEDIUM = "MEDIUM", "Trung bình"
        HIGH = "HIGH", "Cao"
        URGENT = "URGENT", "Khẩn cấp"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ xử lý"
        IN_PROGRESS = "IN_PROGRESS", "Đang sửa chữa"
        RESOLVED = "RESOLVED", "Đã khắc phục"

    reporter = models.ForeignKey(
        "stsv_app.User", on_delete=models.CASCADE, related_name="facility_reports"
    )
    room = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField(
        "Ảnh báo cáo", folder="facility_reports", blank=True, null=True
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.LOW
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    resolved_by = models.ForeignKey(
        "stsv_app.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_facility_reports",
    )
    resolution_image = CloudinaryField(
        "Ảnh sau khắc phục", folder="facility_resolutions", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Các khiếu nại, thắc mắc chung gửi lên Ban quản trị.
class Complaint(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Thấp"
        MEDIUM = "MEDIUM", "Trung bình"
        HIGH = "HIGH", "Cao"
        URGENT = "URGENT", "Khẩn cấp"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ xử lý"
        PROCESSING = "PROCESSING", "Đang giải quyết"
        CLOSED = "CLOSED", "Đã đóng"

    reporter = models.ForeignKey(
        "stsv_app.User", on_delete=models.CASCADE, related_name="complaints"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.LOW
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    resolved_by = models.ForeignKey(
        "stsv_app.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_complaints",
    )
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
