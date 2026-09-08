from rest_framework import status
from django.urls import reverse
from .base import BaseAPITestCase
from stsv_app.models import FeeCampaign, Payment

class FeeCampaignAPITestCase(BaseAPITestCase):
    def test_get_campaigns(self):
        url = reverse('stsv_app:fee-campaign-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_campaign(self):
        url = reverse('stsv_app:fee-campaign-list')
        self.client.force_authenticate(user=self.bancansu)
        data = {
            "title": "Quỹ lớp Test",
            "description": "Mô tả test",
            "amount": 50000.0,
            "is_mandatory": True,
            "bank_name": "MBBank",
            "bank_account_number": "0896719575",
            "bank_account_name": "NGUYEN VAN A"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["title"], "Quỹ lớp Test")


class PaymentAPITestCase(BaseAPITestCase):
    def test_get_payments(self):
        url = reverse('stsv_app:payment-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment_vietqr(self):
        url = reverse('stsv_app:payment-list')
        self.client.force_authenticate(user=self.student)
        campaign = FeeCampaign.objects.first()
        data = {
            "campaign": campaign.id,
            "amount": float(campaign.amount),
            "payment_method": Payment.PaymentMethod.VIETQR
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("vietqr_url", response.data)


class ClassFinanceManagementAPITestCase(BaseAPITestCase):
    def test_class_status(self):
        campaign = FeeCampaign.objects.first()
        url = reverse('stsv_app:class-finance-management-class-status', kwargs={'pk': campaign.id})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("students", response.data)
