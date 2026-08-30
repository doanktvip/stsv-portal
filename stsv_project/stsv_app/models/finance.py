from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator


# Khoản thu phí (Học phí kỳ 1, phí BHYT, phí làm thẻ,...).
class Fee(models.Model):
    class FeeType(models.TextChoices):
        TUITION = "TUITION", "Học phí"
        CLUB_FUND = "CLUB_FUND", "Quỹ CLB"
        YOUTH_UNION_FEE = "YOUTH_UNION_FEE", "Đoàn phí"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    fee_type = models.CharField(max_length=50, choices=FeeType.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")
    is_mandatory = models.BooleanField(default=True)
    creator = models.ForeignKey("stsv_app.User", on_delete=models.CASCADE)
    due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.title} - {self.amount}"


# Giao dịch thanh toán của sinh viên (thanh toán qua VNPay, MoMo).
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ thanh toán"
        SUCCESS = "SUCCESS", "Thành công"
        FAILED = "FAILED", "Thất bại"

    class Method(models.TextChoices):
        VNPAY = "VNPAY", "VNPay"
        MOMO = "MOMO", "MoMo"

    class RefundStatus(models.TextChoices):
        NONE = "NONE", "Không"
        REQUESTED = "REQUESTED", "Yêu cầu hoàn tiền"
        REFUNDED = "REFUNDED", "Đã hoàn tiền"

    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    payment_method = models.CharField(max_length=50, choices=Method.choices)
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    refund_status = models.CharField(
        max_length=20, choices=RefundStatus.choices, default=RefundStatus.NONE
    )
    paid_at = models.DateTimeField(blank=True, null=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"Payment {self.id} - {self.student.student_id} - {self.status}"
