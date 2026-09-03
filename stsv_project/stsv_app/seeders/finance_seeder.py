from django.utils import timezone
from datetime import timedelta
import random
import uuid
from stsv_app.models.finance import Fee, Payment
from stsv_app.models.users import StudentProfile, User
from stsv_app.models.academics import Semester
from django.contrib.contenttypes.models import ContentType


def seed_finance():
    print("--- Seeding Finance Data ---")
    now = timezone.now()
    creator = User.objects.filter(role=User.Role.ORGOFFICER).first()
    semesters = list(Semester.objects.all())
    students = list(StudentProfile.objects.all())

    if not creator or not semesters or not students:
        return

    # Filter out empty students
    students = [s for s in students if s.user.is_active]

    semester_ct = ContentType.objects.get_for_model(Semester)
    
    fees_to_create = []
    # Tạo khoản phí cho TẤT CẢ các học kỳ
    for semester in semesters:
        fees_to_create.append(Fee(
            title=f"Học phí học kỳ {semester.code}",
            description=f"Học phí hệ chính quy học kỳ {semester.code}",
            amount=5000000,
            fee_type=Fee.FeeType.TUITION,
            content_type=semester_ct,
            object_id=semester.id,
            is_mandatory=True,
            creator=creator,
            due_date=semester.start_date + timedelta(days=30)
        ))
        fees_to_create.append(Fee(
            title=f"Đoàn phí học kỳ {semester.code}",
            description=f"Đoàn phí định kỳ {semester.code}",
            amount=50000,
            fee_type=Fee.FeeType.YOUTH_UNION_FEE,
            content_type=semester_ct,
            object_id=semester.id,
            is_mandatory=True,
            creator=creator,
            due_date=semester.start_date + timedelta(days=30)
        ))
        
    if fees_to_create:
        Fee.objects.bulk_create(fees_to_create)

    created_fees = list(Fee.objects.all())
    
    payments_to_create = []
    current_semester = semesters[-1] if semesters else None

    print("Seeding Payments...")
    for student in students:
        for fee in created_fees:
            # Nếu là phí của học kỳ hiện tại -> Chưa đóng (hoặc có GD đang xử lý/thất bại)
            if current_semester and fee.object_id == current_semester.id:
                if random.random() < 0.2:  # 20% có GD lỗi
                    status = random.choice([Payment.Status.FAILED, Payment.Status.PENDING])
                    method = random.choice(Payment.Method.choices)[0]
                    payments_to_create.append(Payment(
                        student=student,
                        fee=fee,
                        amount=fee.amount,
                        status=status,
                        payment_method=method,
                        transaction_id=f"{method}_{uuid.uuid4().hex[:8].upper()}",
                        refund_status=Payment.RefundStatus.NONE,
                    ))
            else:
                # Các kỳ cũ -> Đã thanh toán thành công
                method = random.choice(Payment.Method.choices)[0]
                paid_at = fee.due_date - timedelta(days=random.randint(1, 20))
                payments_to_create.append(Payment(
                    student=student,
                    fee=fee,
                    amount=fee.amount,
                    status=Payment.Status.SUCCESS,
                    payment_method=method,
                    transaction_id=f"{method}_{uuid.uuid4().hex[:8].upper()}",
                    refund_status=Payment.RefundStatus.NONE,
                    paid_at=paid_at
                ))

    if payments_to_create:
        Payment.objects.bulk_create(payments_to_create)

    print("Finance data seeded successfully.")
