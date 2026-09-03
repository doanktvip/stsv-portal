from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from stsv_app.models.finance import Payment
from .factory import PaymentFactory


class UnifiedWebhookView(views.APIView):
    """
    Webhook hợp nhất xử lý phản hồi từ TẤT CẢ các cổng thanh toán.
    Tự động route đến đúng class Provider (MoMo, VNPay, v.v.) dựa vào URL parameter.
    """
    permission_classes = [AllowAny]

    def post(self, request, provider_name):
        return self._process_webhook(request, provider_name, request.data)

    def get(self, request, provider_name):
        return self._process_webhook(request, provider_name, request.query_params.dict())

    def _process_webhook(self, request, provider_name, data):
        try:
            provider = PaymentFactory.get_payment_gateway(provider_name)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Trích xuất Transaction ID theo từng provider (MOMO dùng orderId, VNPAY dùng vnp_TxnRef)
        transaction_id = data.get('orderId') if provider_name.upper() == 'MOMO' else data.get('vnp_TxnRef')
        
        if not transaction_id:
            return Response({"detail": "Missing Transaction ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Xác thực chữ ký bằng Provider tương ứng
        if not provider.verify_webhook(data):
            return Response({"detail": "Xác thực chữ ký thất bại."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                # Lock row payment để tránh conflict nếu nhận được request đồng thời
                payment = Payment.objects.select_for_update().get(transaction_id=transaction_id)
                
                if payment.status == Payment.Status.SUCCESS:
                    return Response({"detail": "Đơn hàng đã được thanh toán."}, status=status.HTTP_200_OK)

                # TODO: Kiểm tra số tiền (amount) nếu cần thiết
                
                payment.status = Payment.Status.SUCCESS
                payment.paid_at = timezone.now()
                payment.gateway_response = data
                payment.save(update_fields=['status', 'paid_at', 'gateway_response'])
                
            return Response({"detail": "Thanh toán thành công!"}, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response({"detail": "Không tìm thấy giao dịch."}, status=status.HTTP_404_NOT_FOUND)
