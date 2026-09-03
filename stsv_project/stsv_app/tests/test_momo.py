from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from stsv_app.services.payments.providers.momo import MoMoProvider
import requests
import hmac
import hashlib

@override_settings(MOMO_CONFIG={
    'PARTNER_CODE': 'TESTCODE',
    'ACCESS_KEY': 'TESTACCESS',
    'SECRET_KEY': 'TESTSECRET',
    'NOTIFY_URL': 'https://test.com/notify',
    'ENDPOINT': 'https://test.com/endpoint'
})
class MoMoProviderTestCase(TestCase):
    def setUp(self):
        self.provider = MoMoProvider()

    @patch('stsv_app.services.payments.providers.momo.requests.post')
    def test_generate_payment_url_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"payUrl": "https://momo.vn/pay"}
        mock_post.return_value = mock_response

        url = self.provider.generate_payment_url(
            transaction_id="ORDER123",
            amount=100000,
            order_info="Test Order",
            return_url="https://test.com/return"
        )
        self.assertEqual(url, "https://momo.vn/pay")
        mock_post.assert_called_once()

    @patch('stsv_app.services.payments.providers.momo.requests.post')
    def test_generate_payment_url_api_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            self.provider.generate_payment_url(
                transaction_id="ORDER123",
                amount=100000,
                order_info="Test Order",
                return_url="https://test.com/return"
            )

    @patch('stsv_app.services.payments.providers.momo.requests.post')
    def test_generate_payment_url_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        with self.assertRaises(ValueError):
            self.provider.generate_payment_url(
                transaction_id="ORDER123",
                amount=100000,
                order_info="Test Order",
                return_url="https://test.com/return"
            )

    @override_settings(MOMO_CONFIG={})
    def test_generate_payment_url_no_config(self):
        """Khi không có config MoMo, trả về mock redirect về return_url với resultCode=0."""
        url = self.provider.generate_payment_url(
            transaction_id="ORDER123",
            amount=100000,
            order_info="Test Order",
            return_url="https://test.com/return"
        )
        self.assertTrue(url.startswith("https://test.com/return"))
        self.assertIn("resultCode=0", url)

    def test_verify_webhook_success(self):
        # We need to construct a valid signature for the test
        request_data = {
            'resultCode': 0,
            'partnerCode': 'TESTCODE',
            'orderId': 'ORDER123',
            'requestId': 'REQ123',
            'amount': '100000',
            'orderInfo': 'Test Order',
            'orderType': 'momo_wallet',
            'transId': 'TRANS123',
            'message': 'Success',
            'payType': 'qr',
            'responseTime': '1234567890',
            'extraData': ''
        }
        
        raw_data = (
            f"accessKey=TESTACCESS"
            f"&amount=100000"
            f"&extraData="
            f"&message=Success"
            f"&orderId=ORDER123"
            f"&orderInfo=Test Order"
            f"&orderType=momo_wallet"
            f"&partnerCode=TESTCODE"
            f"&payType=qr"
            f"&requestId=REQ123"
            f"&responseTime=1234567890"
            f"&resultCode=0"
            f"&transId=TRANS123"
        )
        
        signature = hmac.new(
            'TESTSECRET'.encode('utf-8'),
            raw_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request_data['signature'] = signature
        
        self.assertTrue(self.provider.verify_webhook(request_data))

    def test_verify_webhook_invalid_signature(self):
        request_data = {
            'resultCode': 0,
            'signature': 'invalid_signature'
        }
        self.assertFalse(self.provider.verify_webhook(request_data))

    def test_verify_webhook_failed_result_code(self):
        request_data = {
            'resultCode': 1006
        }
        self.assertFalse(self.provider.verify_webhook(request_data))
