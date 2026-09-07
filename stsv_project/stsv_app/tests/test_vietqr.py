from django.test import TestCase
from stsv_app.models import FeeCampaign

class VietQRTestCase(TestCase):
    def test_vietqr_url_generation(self):
        campaign = FeeCampaign.objects.create(
            title="Đoàn phí HK1",
            amount=24000,
            bank_name="MBBank",
            bank_account_number="0896719575",
            bank_account_name="NGUYEN VAN DOAN"
        )
        url = campaign.get_vietqr_url(student_code="2151010001", amount=24000)
        self.assertIn("img.vietqr.io", url)
        self.assertIn("MBBank-0896719575", url)
        self.assertIn("amount=24000", url)
