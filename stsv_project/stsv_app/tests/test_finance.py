from rest_framework import status
from django.urls import reverse
from stsv_app.tests.base import BaseAPITestCase
from stsv_app.models.finance import Fee, Payment

class FeeAPITestCase(BaseAPITestCase):
    def test_get_fees(self):
        url = reverse('stsv_app:fee-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentAPITestCase(BaseAPITestCase):
    def test_get_payments(self):
        url = reverse('stsv_app:payment-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment_momo(self):
        url = reverse('stsv_app:payment-list')
        self.client.force_authenticate(user=self.student)
        # Lấy một khoản phí bất kỳ để thanh toán
        fee = Fee.objects.first()
        data = {
            "fee": fee.id,
            "amount": float(fee.amount),
            "payment_method": Payment.Method.MOMO,
            "return_url": "stsvapp://test-return"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment_url", response.data)

    def test_refund_payment_success(self):
        self.client.force_authenticate(user=self.student)
        # Tìm một giao dịch SUCCESS của sinh viên này
        payment = Payment.objects.filter(
            student=self.student.student_profile, 
            status=Payment.Status.SUCCESS,
            refund_status=Payment.RefundStatus.NONE
        ).first()
        
        url = reverse('stsv_app:payment-refund', kwargs={'pk': payment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refund_payment_invalid_status(self):
        self.client.force_authenticate(user=self.student)
        # Tự tạo một payment PENDING để test không phụ thuộc vào seeder
        fee = Fee.objects.first()
        payment = Payment.objects.create(
            student=self.student.student_profile,
            fee=fee,
            amount=fee.amount,
            status=Payment.Status.PENDING,
            payment_method=Payment.Method.MOMO,
            transaction_id="TEST-PENDING-REFUND-001",
            refund_status=Payment.RefundStatus.NONE,
        )

        url = reverse('stsv_app:payment-refund', kwargs={'pk': payment.id})
        response = self.client.post(url)
        # Bắt buộc phải SUCCESS mới được refund, nên sẽ trả về 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminFinanceAPITestCase(BaseAPITestCase):
    def test_overview(self):
        url = reverse('stsv_app:admin-finance-overview')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_revenue", response.data)

    def test_revenue_by_type(self):
        url = reverse('stsv_app:admin-finance-revenue-by-type')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recent_transactions(self):
        url = reverse('stsv_app:admin-finance-recent-transactions')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
