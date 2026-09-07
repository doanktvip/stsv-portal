import random
import uuid
from django.utils import timezone
from datetime import timedelta
from stsv_app.models import FeeCampaign, Payment, StudentProfile, User, Semester


def seed_finance():
    print("--- Nạp Dữ Liệu Tài Chính & Học Phí ---")
    creator = User.objects.filter(role=User.Role.ORGOFFICER).first()
    if not creator:
        creator = User.objects.first()

    semesters = list(Semester.objects.all())
    students = list(StudentProfile.objects.filter(user__is_active=True))

    if not creator or not students:
        return

    # Xóa dữ liệu cũ
    Payment.objects.all().delete()
    FeeCampaign.objects.all().delete()

    fees_to_create = [
        FeeCampaign(
            title="Đoàn phí Học kỳ I (Năm học 2025 - 2026)",
            description="Thu đoàn phí định kỳ học kỳ 1 cho toàn thể đoàn viên, sinh viên theo quy định của Đoàn trường.",
            amount=24000,
            is_mandatory=True,
            creator=creator,
            bank_name="MBBank",
            bank_account_number="0896719575",
            bank_account_name="NGUYEN VAN DOAN",
            due_date=timezone.now() + timedelta(days=30)
        ),
        FeeCampaign(
            title="Quỹ hoạt động Chi đoàn & Sinh hoạt lớp",
            description="Kinh phí tổ chức sinh hoạt lớp, khen thưởng phong trào học tập và liên hoan cuối kỳ.",
            amount=50000,
            is_mandatory=False,
            creator=creator,
            bank_name="MBBank",
            bank_account_number="0896719575",
            bank_account_name="NGUYEN VAN DOAN",
            due_date=timezone.now() + timedelta(days=45)
        ),
        FeeCampaign(
            title="Quyên góp ủng hộ Chiến dịch Xuân Tình Nguyện 2026",
            description="Kinh phí hỗ trợ các phần quà Tết cho bà con có hoàn cảnh khó khăn tại vùng sâu vùng xa.",
            amount=30000,
            is_mandatory=False,
            creator=creator,
            bank_name="MBBank",
            bank_account_number="0896719575",
            bank_account_name="NGUYEN VAN DOAN",
            due_date=timezone.now() + timedelta(days=60)
        )
    ]

    FeeCampaign.objects.bulk_create(fees_to_create)
    created_fees = list(FeeCampaign.objects.all())
    
    payments_to_create = []
    print("Đang nạp các giao dịch thanh toán VietQR và Tiền mặt...")
    
    for student in students:
        for campaign in created_fees:
            rand_val = random.random()
            if rand_val < 0.35:
                # Chưa nộp (không tạo payment)
                continue
            elif rand_val < 0.70:
                # Thành công qua VietQR
                paid_at = timezone.now() - timedelta(days=random.randint(1, 10))
                payments_to_create.append(Payment(
                    student=student,
                    campaign=campaign,
                    amount=campaign.amount,
                    payment_method=Payment.PaymentMethod.VIETQR,
                    status=Payment.Status.SUCCESS,
                    transaction_id=f"VQR_{student.student_id}_{campaign.id}_{uuid.uuid4().hex[:6].upper()}",
                    paid_at=paid_at,
                    notes="Thanh toán qua quét mã VietQR thành công"
                ))
            else:
                # Nộp tiền mặt trực tiếp cho Thủ quỹ
                paid_at = timezone.now() - timedelta(days=random.randint(1, 15))
                payments_to_create.append(Payment(
                    student=student,
                    campaign=campaign,
                    amount=campaign.amount,
                    payment_method=Payment.PaymentMethod.CASH,
                    status=Payment.Status.SUCCESS,
                    transaction_id=f"CASH_{student.student_id}_{campaign.id}_{uuid.uuid4().hex[:6].upper()}",
                    paid_at=paid_at,
                    notes="Đã thu tiền mặt trực tiếp"
                ))

    if payments_to_create:
        Payment.objects.bulk_create(payments_to_create)

    print("Nạp dữ liệu tài chính thành công.")

