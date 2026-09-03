import hmac
import hashlib
import requests
import uuid
import logging
import urllib.parse as up
from django.conf import settings
from ..base import BasePaymentProvider

logger = logging.getLogger(__name__)

class MoMoProvider(BasePaymentProvider):
    def generate_payment_url(self, transaction_id: str, amount: float, order_info: str, return_url: str, **kwargs) -> str:
        config = getattr(settings, 'MOMO_CONFIG', {})
        if not config or not config.get('PARTNER_CODE'):
            # Giả lập trả về Deep Link thành công
            safe_msg = up.quote("Giao dịch giả lập thành công")
            target_url = f"{return_url}?resultCode=0&message={safe_msg}"
            mock_base = kwargs.get('mock_redirect_base')
            if mock_base:
                return f"{mock_base}?return_url={up.quote(target_url)}"
            return target_url

        request_id = str(uuid.uuid4())
        extra_data = ""
        # captureWallet is standard for Momo App-to-App
        request_type = "captureWallet"

        raw_signature = (
            f"accessKey={config.get('ACCESS_KEY', '')}"
            f"&amount={int(amount)}"
            f"&extraData={extra_data}"
            f"&ipnUrl={config.get('NOTIFY_URL', '')}"
            f"&orderId={transaction_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={config.get('PARTNER_CODE', '')}"
            f"&redirectUrl={return_url}"
            f"&requestId={request_id}"
            f"&requestType={request_type}"
        )

        signature = hmac.new(
            config.get('SECRET_KEY', '').encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        payload = {
            "partnerCode": config.get('PARTNER_CODE', ''),
            "partnerName": "STSV Portal",
            "storeId": "STSV-Portal-Store",
            "requestId": request_id,
            "amount": int(amount),
            "orderId": transaction_id,
            "orderInfo": order_info,
            "redirectUrl": return_url,
            "ipnUrl": config.get('NOTIFY_URL', ''),
            "lang": "vi",
            "extraData": extra_data,
            "requestType": request_type,
            "signature": signature
        }

        try:
            endpoint = config.get('ENDPOINT', 'https://test-payment.momo.vn/v2/gateway/api/create')
            response = requests.post(endpoint, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Lỗi MoMo: {response.status_code} - {response.text}")
                raise ValueError(f"MoMo Error: {response.text}")
                
            response.raise_for_status()
            res_data = response.json()
            
            return res_data.get("payUrl", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gọi API MoMo: {e}")
            raise ValueError(f"Không thể kết nối đến cổng thanh toán MoMo lúc này. Lỗi: {str(e)}")

    def verify_webhook(self, request_data: dict) -> bool:
        if request_data.get('resultCode') != 0:
            return False

        config = getattr(settings, 'MOMO_CONFIG', {})
        if not config or not config.get('PARTNER_CODE'):
            return True # Mock for testing

        partner_code = request_data.get('partnerCode', '')
        order_id = request_data.get('orderId', '')
        request_id = request_data.get('requestId', '')
        amount = request_data.get('amount', '')
        order_info = request_data.get('orderInfo', '')
        order_type = request_data.get('orderType', '')
        trans_id = request_data.get('transId', '')
        result_code = request_data.get('resultCode', '')
        message = request_data.get('message', '')
        pay_type = request_data.get('payType', '')
        response_time = request_data.get('responseTime', '')
        extra_data = request_data.get('extraData', '')
        momo_signature = request_data.get('signature', '')

        raw_data = (
            f"accessKey={config.get('ACCESS_KEY', '')}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&message={message}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&orderType={order_type}"
            f"&partnerCode={partner_code}"
            f"&payType={pay_type}"
            f"&requestId={request_id}"
            f"&responseTime={response_time}"
            f"&resultCode={result_code}"
            f"&transId={trans_id}"
        )

        my_signature = hmac.new(
            config.get('SECRET_KEY', '').encode('utf-8'),
            raw_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if my_signature == momo_signature:
            return True
        else:
            logger.warning(f"Cảnh báo bảo mật: Sai chữ ký IPN MoMo! Order ID: {order_id}")
            return False
