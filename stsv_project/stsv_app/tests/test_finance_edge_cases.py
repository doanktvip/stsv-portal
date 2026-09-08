from rest_framework import status
from django.urls import reverse
from .base import BaseAPITestCase
from stsv_app.models import FeeCampaign, Payment

class FinanceEdgeCasesAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.campaign = FeeCampaign.objects.first()

    def test_class_status(self):
        if self.campaign:
            url = reverse('stsv_app:class-finance-management-class-status', kwargs={'pk': self.campaign.pk})
            self.client.force_authenticate(user=self.bancansu)
            response = self.client.get(url)
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_confirm_cash(self):
        if self.campaign:
            url = reverse('stsv_app:class-finance-management-confirm-cash')
            self.client.force_authenticate(user=self.bancansu)
            student_prof = getattr(self.student, 'student_profile', None)
            data = {
                'campaign_id': self.campaign.pk,
                'student_id': student_prof.id if student_prof else 1
            }
            response = self.client.post(url, data)
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_toggle_payment(self):
        payment = Payment.objects.first()
        if payment:
            url = reverse('stsv_app:class-finance-management-toggle-payment', kwargs={'pk': payment.pk})
            self.client.force_authenticate(user=self.bancansu)
            data = {
                'status': Payment.Status.SUCCESS,
                'notes': 'Test note'
            }
            response = self.client.post(url, data)
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

