from django.db import models


class ServiceRequest(models.Model):
    class ServiceType(models.TextChoices):
        ENROLLMENT_CERT = "ENROLLMENT_CERT", "Giấy xác nhận sinh viên"
        TRANSCRIPT = "TRANSCRIPT", "Bảng điểm"
        LEAVE_OF_ABSENCE = "LEAVE_OF_ABSENCE", "Đơn xin tạm nghỉ học"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ xử lý"
        PROCESSING = "PROCESSING", "Đang xử lý"
        READY_FOR_PICKUP = "READY_FOR_PICKUP", "Đã có kết quả"
        DONE = "DONE", "Đã hoàn thành"
        REJECTED = "REJECTED", "Từ chối"

    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=ServiceType.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    attached_files = models.JSONField(blank=True, null=True)
    response_file = models.FileField(
        upload_to="service_responses/", blank=True, null=True
    )
    expected_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.id} - {self.student.student_id} - {self.service_type}"


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
    image = models.ImageField(upload_to="facility_reports/", blank=True, null=True)
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
    resolution_image = models.ImageField(
        upload_to="facility_resolutions/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
