from django.utils import timezone
from .base import BaseService
from .exceptions import ValidationError, ResourceNotFoundError
from stsv_app.models import FeeCampaign, Payment, StudentProfile, User, HomeroomClass
from django.db.models import Count, Q, Prefetch


class FinanceService(BaseService):
    def get_campaigns_for_user(self, user: User):

        base_qs = FeeCampaign.objects.select_related('creator', 'homeroom_class').annotate(
            paid_count_annotated=Count('payments', filter=Q(payments__status=Payment.Status.SUCCESS), distinct=True),
            total_students_annotated=Count('homeroom_class__students', distinct=True)
        )

        if hasattr(user, 'student_profile'):
            student = user.student_profile
            base_qs = base_qs.prefetch_related(
                Prefetch(
                    'payments',
                    queryset=Payment.objects.filter(student=student),
                    to_attr='_prefetched_user_payments'
                )
            )
            if student.homeroom_class:
                return base_qs.filter(
                    Q(homeroom_class=student.homeroom_class) | Q(homeroom_class__isnull=True)
                ).order_by('-created_at')

        return base_qs.order_by('-created_at')

    def create_fee_campaign(self, creator: User, validated_data: dict) -> FeeCampaign:
        homeroom_class = None
        if hasattr(creator, 'student_profile') and creator.student_profile.homeroom_class:
            homeroom_class = creator.student_profile.homeroom_class

        campaign = FeeCampaign.objects.create(
            creator=creator,
            homeroom_class=homeroom_class,
            **validated_data
        )
        return campaign

    def initiate_payment(self, user: User, campaign_id: int, amount: float = None, payment_method: str = Payment.PaymentMethod.VIETQR, notes: str = '') -> dict:
        if not hasattr(user, 'student_profile'):
            raise ValidationError("Chỉ sinh viên mới có thể thực hiện đóng quỹ.")

        student = user.student_profile
        campaign = FeeCampaign.objects.filter(id=campaign_id).first()
        if not campaign:
            raise ResourceNotFoundError("Không tìm thấy đợt thu quỹ.")

        pay_amount = amount if amount is not None else campaign.amount

        payment, created = Payment.objects.get_or_create(
            campaign=campaign,
            student=student,
            defaults={
                'amount': pay_amount,
                'payment_method': payment_method,
                'status': Payment.Status.PENDING,
                'notes': notes,
                'transaction_id': f"TXN_{student.student_id}_{campaign.id}_{int(timezone.now().timestamp())}"
            }
        )

        if not created:
            payment.amount = pay_amount
            payment.payment_method = payment_method
            payment.notes = notes
            payment.save()

        # Tự động sinh link ảnh VietQR
        vietqr_url = campaign.get_vietqr_url(student_code=student.student_id, amount=int(pay_amount))

        return {
            'id': payment.id,
            'campaign_id': campaign.id,
            'campaign_title': campaign.title,
            'amount': payment.amount,
            'payment_method': payment.payment_method,
            'status': payment.status,
            'vietqr_url': vietqr_url,
            'message': 'Khởi tạo thông tin thanh toán VietQR thành công'
        }

    def get_class_finance_status(self, user: User, campaign_id: int) -> dict:
        campaign = FeeCampaign.objects.filter(id=campaign_id).first()
        if not campaign:
            raise ResourceNotFoundError("Không tìm thấy đợt thu quỹ.")

        homeroom_class = campaign.homeroom_class
        if not homeroom_class and hasattr(user, 'student_profile') and user.student_profile.homeroom_class:
            homeroom_class = user.student_profile.homeroom_class
        if not homeroom_class:
            homeroom_class = HomeroomClass.objects.first()

        if not homeroom_class:
            raise ValidationError("Không tìm thấy lớp học áp dụng.")

        students = StudentProfile.objects.filter(homeroom_class=homeroom_class).select_related('user')
        payments = {p.student_id: p for p in Payment.objects.filter(campaign=campaign)}

        result = []
        for s in students:
            p = payments.get(s.id)
            result.append({
                'student_id': s.id,
                'student_code': s.student_id,
                'student_name': s.user.get_full_name() or s.user.username,
                'payment_id': p.id if p else None,
                'status': p.status if p else 'UNPAID',
                'payment_method': p.payment_method if p else None,
                'amount': p.amount if p else campaign.amount,
                'paid_at': p.paid_at if p else None,
            })

        return {
            'campaign_id': campaign.id,
            'campaign_title': campaign.title,
            'amount': campaign.amount,
            'homeroom_class': homeroom_class.name,
            'total_students': len(students),
            'paid_count': sum(1 for item in result if item['status'] == Payment.Status.SUCCESS),
            'students': result
        }

    def confirm_cash_payment(self, user: User, campaign_id: int, student_id: int, notes: str = '') -> Payment:
        campaign = FeeCampaign.objects.filter(id=campaign_id).first()
        student = StudentProfile.objects.filter(id=student_id).first()

        if not campaign or not student:
            raise ValidationError("Khoản thu hoặc sinh viên không hợp lệ.")

        payment, _ = Payment.objects.get_or_create(
            campaign=campaign,
            student=student,
            defaults={
                'amount': campaign.amount,
                'payment_method': Payment.PaymentMethod.CASH,
                'status': Payment.Status.SUCCESS,
                'paid_at': timezone.now(),
                'notes': notes or 'Đã nộp tiền mặt trực tiếp cho Lớp trưởng'
            }
        )
        payment.payment_method = Payment.PaymentMethod.CASH
        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        payment.notes = notes or 'Đã nộp tiền mặt trực tiếp cho Lớp trưởng'
        payment.save()

        return payment

    def toggle_payment_status(self, user: User, payment_id: int, target_status: str, notes: str = '') -> Payment:
        payment = Payment.objects.filter(id=payment_id).first()
        if not payment:
            raise ResourceNotFoundError("Không tìm thấy giao dịch thanh toán.")

        payment.status = target_status
        payment.notes = notes
        if target_status == Payment.Status.SUCCESS:
            payment.paid_at = timezone.now()
        else:
            payment.paid_at = None
        payment.save()

        return payment
