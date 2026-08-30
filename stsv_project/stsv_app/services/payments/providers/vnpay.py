import hashlib
import hmac
import urllib.parse
from datetime import datetime
from django.conf import settings
from ..base import BasePaymentProvider

class VNPayProvider(BasePaymentProvider):
    def generate_payment_url(self, transaction_id: str, amount: float, order_info: str, return_url: str) -> str:
        config = getattr(settings, 'VNPAY_CONFIG', {})
        if not config or not config.get('TMN_CODE'):
            return f"https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?id={transaction_id}&amount={amount}"

        vnp_TmnCode = config.get('TMN_CODE', '')
        vnp_HashSecret = config.get('HASH_SECRET', '')
        vnp_Url = config.get('ENDPOINT', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
        
        input_data = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": vnp_TmnCode,
            "vnp_Amount": str(int(amount * 100)), # VNPay nhân 100
            "vnp_CreateDate": datetime.now().strftime('%Y%m%d%H%M%S'),
            "vnp_CurrCode": "VND",
            "vnp_IpAddr": "127.0.0.1",
            "vnp_Locale": "vn",
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "other",
            "vnp_ReturnUrl": return_url,
            "vnp_TxnRef": transaction_id,
        }

        # Sắp xếp khóa
        query_string = ''
        seq = 0
        for key, val in sorted(input_data.items()):
            if seq == 1:
                query_string += "&"
            query_string += f"{key}={urllib.parse.quote_plus(str(val))}"
            seq = 1

        hash_value = hmac.new(
            vnp_HashSecret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        payment_url = f"{vnp_Url}?{query_string}&vnp_SecureHash={hash_value}"
        return payment_url

    def verify_webhook(self, request_data: dict) -> bool:
        config = getattr(settings, 'VNPAY_CONFIG', {})
        if not config or not config.get('TMN_CODE'):
            return True # Mock for testing

        vnp_HashSecret = config.get('HASH_SECRET', '')
        vnp_SecureHash = request_data.pop('vnp_SecureHash', '')
        
        # Bỏ đi vnp_SecureHashType nếu có
        if 'vnp_SecureHashType' in request_data:
            request_data.pop('vnp_SecureHashType')

        input_data = dict(sorted(request_data.items()))
        
        query_string = ''
        seq = 0
        for key, val in input_data.items():
            if seq == 1:
                query_string += "&"
            query_string += f"{key}={urllib.parse.quote_plus(str(val))}"
            seq = 1

        my_hash = hmac.new(
            vnp_HashSecret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        if my_hash == vnp_SecureHash:
            # Check response code
            if request_data.get('vnp_ResponseCode') == '00':
                return True
        return False
