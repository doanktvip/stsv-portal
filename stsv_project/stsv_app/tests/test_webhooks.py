from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from .base import BaseAPITestCase
from django.contrib.contenttypes.models import ContentType
from stsv_app.models.finance import Payment, Fee

class WebhookAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        
        # Tạo fee và payment
        self.fee = Fee.objects.create(
            title="Học phí HK1",
            amount=5000000,
            fee_type=Fee.FeeType.TUITION,
            content_type=ContentType.objects.get_for_model(self.student),
            object_id=self.student.id,
            creator=self.admin,
            due_date="2027-01-01 00:00:00"
        )
        self.payment = Payment.objects.create(
            fee=self.fee,
            student=self.student.student_profile,
            amount=5000000,
            transaction_id="TXN123",
            status=Payment.Status.PENDING
        )

    def test_webhook_invalid_provider(self):
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'INVALID'})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Phương thức thanh toán INVALID không được hỗ trợ.")

    def test_webhook_missing_transaction_id(self):
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'MOMO'})
        response = self.client.post(url, {"amount": 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Missing Transaction ID.")

    @patch('stsv_app.services.payments.providers.momo.MoMoProvider.verify_webhook')
    def test_webhook_momo_invalid_signature(self, mock_verify):
        mock_verify.return_value = False
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'MOMO'})
        response = self.client.post(url, {"orderId": "TXN123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Xác thực chữ ký thất bại.")

    @patch('stsv_app.services.payments.providers.momo.MoMoProvider.verify_webhook')
    def test_webhook_momo_success(self, mock_verify):
        mock_verify.return_value = True
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'MOMO'})
        response = self.client.post(url, {"orderId": "TXN123", "amount": 5000000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Thanh toán thành công!")
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.SUCCESS)

    @patch('stsv_app.services.payments.providers.vnpay.VNPayProvider.verify_webhook')
    def test_webhook_vnpay_success_get(self, mock_verify):
        mock_verify.return_value = True
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'VNPAY'})
        response = self.client.get(url, {"vnp_TxnRef": "TXN123", "vnp_Amount": 500000000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.SUCCESS)

    @patch('stsv_app.services.payments.providers.momo.MoMoProvider.verify_webhook')
    def test_webhook_payment_not_found(self, mock_verify):
        mock_verify.return_value = True
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'MOMO'})
        response = self.client.post(url, {"orderId": "NON_EXISTING"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('stsv_app.services.payments.providers.momo.MoMoProvider.verify_webhook')
    def test_webhook_already_paid(self, mock_verify):
        mock_verify.return_value = True
        self.payment.status = Payment.Status.SUCCESS
        self.payment.save()
        
        url = reverse('stsv_app:finance-webhook', kwargs={'provider_name': 'MOMO'})
        response = self.client.post(url, {"orderId": "TXN123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Đơn hàng đã được thanh toán.")
