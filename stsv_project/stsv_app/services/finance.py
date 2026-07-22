from .base import BaseService
from stsv_app.models.finance import Fee, Payment
from .exceptions import ResourceNotFoundError, ValidationError
from django.utils import timezone

class FinanceService(BaseService):
    def get_student_fees(self, student_profile_id: int):
        # Lưu ý: target_id của generic relation sẽ phức tạp hơn chút, đây là code demo.
        return Fee.objects.all()
        
    @BaseService.run_in_transaction
    def process_fee_payment(self, student_id: int, fee_id: int, amount: float, method: str) -> Payment:
        try:
            fee = Fee.objects.get(id=fee_id)
        except Fee.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy khoản phí.")
            
        payment = Payment(
            student_id=student_id,
            fee=fee,
            amount=amount,
            status=Payment.Status.SUCCESS,
            payment_method=method,
            paid_at=timezone.now()
        )
        payment.save()
        return payment
