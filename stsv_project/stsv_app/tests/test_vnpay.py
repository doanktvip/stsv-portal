from django.test import TestCase, override_settings
from stsv_app.services.payments.providers.vnpay import VNPayProvider
import urllib.parse
import hmac
import hashlib

@override_settings(VNPAY_CONFIG={
    'TMN_CODE': 'TESTTMN',
    'HASH_SECRET': 'TESTSECRET',
    'ENDPOINT': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
})
class VNPayProviderTestCase(TestCase):
    def setUp(self):
        self.provider = VNPayProvider()

    def test_generate_payment_url_success(self):
        url = self.provider.generate_payment_url(
            transaction_id="ORDER123",
            amount=100000,
            order_info="Test Order VNPay",
            return_url="https://test.com/vnpay/return"
        )
        self.assertTrue(url.startswith("https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?"))
        self.assertIn("vnp_Amount=10000000", url)
        self.assertIn("vnp_TmnCode=TESTTMN", url)
        self.assertIn("vnp_SecureHash=", url)

    @override_settings(VNPAY_CONFIG={})
    def test_generate_payment_url_no_config(self):
        """Khi không có config VNPay, trả về mock redirect về return_url với vnp_ResponseCode=00."""
        url = self.provider.generate_payment_url(
            transaction_id="ORDER123",
            amount=100000,
            order_info="Test Order VNPay",
            return_url="https://test.com/vnpay/return"
        )
        self.assertTrue(url.startswith("https://test.com/vnpay/return"))
        self.assertIn("vnp_ResponseCode=00", url)

    def test_verify_webhook_success(self):
        request_data = {
            'vnp_Amount': '10000000',
            'vnp_Command': 'pay',
            'vnp_CreateDate': '20231010101010',
            'vnp_CurrCode': 'VND',
            'vnp_IpAddr': '127.0.0.1',
            'vnp_Locale': 'vn',
            'vnp_OrderInfo': 'Test Order VNPay',
            'vnp_OrderType': 'other',
            'vnp_ReturnUrl': 'https://test.com/vnpay/return',
            'vnp_TmnCode': 'TESTTMN',
            'vnp_TxnRef': 'ORDER123',
            'vnp_ResponseCode': '00'
        }
        
        input_data = dict(sorted(request_data.items()))
        query_string = ''
        seq = 0
        for key, val in input_data.items():
            if seq == 1:
                query_string += "&"
            query_string += f"{key}={urllib.parse.quote_plus(str(val))}"
            seq = 1

        hash_value = hmac.new(
            'TESTSECRET'.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        request_data['vnp_SecureHash'] = hash_value
        request_data['vnp_SecureHashType'] = 'SHA512'

        self.assertTrue(self.provider.verify_webhook(request_data))

    def test_verify_webhook_invalid_signature(self):
        request_data = {
            'vnp_ResponseCode': '00',
            'vnp_SecureHash': 'invalid_hash'
        }
        self.assertFalse(self.provider.verify_webhook(request_data))

    def test_verify_webhook_failed_response_code(self):
        request_data = {
            'vnp_ResponseCode': '24',
            'another_key': 'value',
        }
        
        input_data = dict(sorted(request_data.items()))
        query_string = ''
        seq = 0
        for key, val in input_data.items():
            if seq == 1:
                query_string += "&"
            query_string += f"{key}={urllib.parse.quote_plus(str(val))}"
            seq = 1

        hash_value = hmac.new(
            'TESTSECRET'.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        request_data['vnp_SecureHash'] = hash_value
        
        self.assertFalse(self.provider.verify_webhook(request_data))
