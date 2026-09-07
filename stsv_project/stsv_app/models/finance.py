import urllib.parse
from django.db import models
from django.core.validators import MinValueValidator

# Khoản thu quỹ lớp, đoàn phí, quỹ phong trào sinh viên
class FeeCampaign(models.Model):
    class BankChoice(models.TextChoices):
        MB = "MBBank", "MBBank - Ngân hàng Quân Đội"
        VCB = "VCB", "Vietcombank - Ngân hàng Ngoại Thương"
        TCB = "Techcombank", "Techcombank - Ngân hàng Kỹ Thương"
        ICB = "VietinBank", "VietinBank - Ngân hàng Công Thương"
        BIDV = "BIDV", "BIDV - Đầu tư và Phát triển"
        VBA = "Agribank", "Agribank - Nông nghiệp & PTNT"
        ACB = "ACB", "ACB - Ngân hàng Á Châu"
        TPB = "TPBank", "TPBank - Ngân hàng Tiên Phong"
        VPB = "VPBank", "VPBank - Việt Nam Thịnh Vượng"
        STB = "Sacombank", "Sacombank - Sài Gòn Thương Tín"
        HDB = "HDBank", "HDBank - Phát triển TP.HCM"
        VIB = "VIB", "VIB - Ngân hàng Quốc Tế"
        MSB = "MSB", "MSB - Ngân hàng Hàng Hải"
        OCB = "OCB", "OCB - Ngân hàng Phương Đông"
        SHB = "SHB", "SHB - Sài Gòn Hà Nội"
    title = models.CharField(max_length=255, verbose_name="Tên đợt thu")
    description = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Số tiền (VNĐ)"
    )
    is_mandatory = models.BooleanField(default=True, verbose_name="Bắt buộc")
    creator = models.ForeignKey("stsv_app.User", on_delete=models.CASCADE, null=True, verbose_name="Người tạo")
    homeroom_class = models.ForeignKey(
        "stsv_app.HomeroomClass", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="fee_campaigns",
        help_text="Lớp áp dụng (để trống nếu áp dụng toàn trường/khoa)"
    )
    
    # Thông tin tài khoản nhận chuyển khoản của Thủ quỹ/Lớp trưởng
    bank_name = models.CharField(
        max_length=50, 
        choices=BankChoice.choices, 
        default=BankChoice.MB,
        verbose_name="Ngân hàng nhận"
    )
    bank_account_number = models.CharField(
        max_length=50, 
        help_text="Số tài khoản nhận tiền của Thủ quỹ/Lớp trưởng", 
        null=True, blank=True
    )
    bank_account_name = models.CharField(
        max_length=150, 
        help_text="Tên chủ tài khoản nhận (VD: NGUYEN VAN A)", 
        null=True, blank=True
    )
    
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Hạn chót")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.amount:,.0f}đ"

    def get_vietqr_url(self, student_code: str = "SV", amount: int = None) -> str:
        if not self.bank_account_number or not self.bank_name:
            return ""
        pay_amount = int(amount if amount else self.amount)
        content = urllib.parse.quote(f"{student_code} DONG QUY {self.id}")
        acc_name = urllib.parse.quote(self.bank_account_name or "")
        return f"https://img.vietqr.io/image/{self.bank_name}-{self.bank_account_number}-compact2.png?amount={pay_amount}&addInfo={content}&accountName={acc_name}"


# Giao dịch đóng phí của sinh viên
class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        VIETQR = "VIETQR", "Chuyển khoản VietQR"
        CASH = "CASH", "Tiền mặt trực tiếp"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Chờ xác nhận"
        SUCCESS = "SUCCESS", "Đã hoàn thành"

    campaign = models.ForeignKey(FeeCampaign, on_delete=models.CASCADE, related_name="payments", null=True)
    student = models.ForeignKey("stsv_app.StudentProfile", on_delete=models.CASCADE, related_name="payments", null=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], null=True
    )
    payment_method = models.CharField(
        max_length=30, 
        choices=PaymentMethod.choices, 
        default=PaymentMethod.VIETQR
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Mã giao dịch hoặc mã tham chiếu")
    notes = models.TextField(blank=True, help_text="Ghi chú thêm")
    paid_at = models.DateTimeField(blank=True, null=True, db_index=True)

    def __str__(self):
        student_id = self.student.student_id if self.student else "Unknown"
        return f"Payment {self.id} - {student_id} - {self.status}"
