from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.utils import timezone
from django.http import HttpResponse
from stsv_app.models.finance import Fee, Payment
from stsv_app.serializers.finance import FeeSerializer, PaymentSerializer, PaymentCreateSerializer
from stsv_app.permissions import IsStudentRole, IsAdminRole
from stsv_app.services.payments.factory import PaymentFactory
from django.db.models import Sum

class MockRedirectView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return_url = request.GET.get('return_url', '')
        html = f"""
        <html>
            <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body style="text-align:center; padding-top: 50px; font-family: sans-serif;">
                <h3>Đang chuyển hướng về App...</h3>
                <script>
                    setTimeout(function() {{
                        window.location.href = "{return_url}";
                    }}, 1500);
                </script>
                <br>
                <a href="{return_url}" style="padding: 10px 20px; background: #005BAA; color: white; text-decoration: none; border-radius: 8px;">Bấm vào đây nếu trình duyệt không tự chuyển</a>
            </body>
        </html>
        """
        return HttpResponse(html)

class FeeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FeeSerializer
    permission_classes = [IsStudentRole]

    def get_queryset(self):
        return Fee.objects.all()


class PaymentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsStudentRole]

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            return Payment.objects.filter(student=self.request.user.student_profile, is_deleted=False)
        return Payment.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save payment record first
        payment = serializer.save(student=request.user.student_profile)
        payment.transaction_id = f"TXN{payment.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        payment.save(update_fields=['transaction_id'])

        try:
            provider = PaymentFactory.get_payment_gateway(payment.payment_method)
            
            # Return URL cho Mobile (Sử dụng Deep link để app tự động bật lại khi thanh toán xong)
            return_url = request.data.get('return_url')
            if not return_url:
                return_url = 'stsvapp://stsv/payment-return'
                
            mock_redirect_base = request.build_absolute_uri('/api/payments/mock-redirect/')
            payment_url = provider.generate_payment_url(
                transaction_id=payment.transaction_id,
                amount=float(payment.amount),
                order_info=f"Thanh toan {payment.fee.title}",
                return_url=return_url,
                mock_redirect_base=mock_redirect_base
            )
            
            headers = self.get_success_headers(serializer.data)
            
            # Make a copy because serializer.data is immutable
            response_data = dict(serializer.data)
            response_data['payment_url'] = payment_url
            
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=['status'])
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status != Payment.Status.SUCCESS:
            return Response(
                {"detail": "Only successful payments can be refunded."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if payment.refund_status != Payment.RefundStatus.NONE:
            return Response(
                {"detail": "Refund already requested or processed."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.refund_status = Payment.RefundStatus.REQUESTED
        payment.save()
        
        return Response({"detail": "Refund requested successfully."}, status=status.HTTP_200_OK)


class AdminFinanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminRole]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        total_revenue = Payment.objects.filter(status=Payment.Status.SUCCESS).aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_pending = Payment.objects.filter(status=Payment.Status.PENDING).aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_refunded = Payment.objects.filter(
            refund_status__in=[Payment.RefundStatus.REQUESTED, Payment.RefundStatus.REFUNDED]
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            "total_revenue": total_revenue,
            "total_pending": total_pending,
            "total_refunded": total_refunded
        })

    @action(detail=False, methods=['get'], url_path='revenue-by-type')
    def revenue_by_type(self, request):
        revenue_data = Payment.objects.filter(status=Payment.Status.SUCCESS).values(
            'fee__fee_type'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('-total_amount')

        # Translate to standard format
        results = []
        for item in revenue_data:
            fee_type = item['fee__fee_type']
            results.append({
                "fee_type": fee_type,
                "fee_type_display": dict(Fee.FeeType.choices).get(fee_type, fee_type),
                "total_amount": item['total_amount']
            })
            
        return Response(results)

    @action(detail=False, methods=['get'], url_path='recent-transactions')
    def recent_transactions(self, request):
        recent_payments = Payment.objects.all().order_by('-id')[:20]
        # We can reuse the PaymentSerializer, but include student name and fee title.
        # PaymentSerializer currently returns all fields.
        serializer = PaymentSerializer(recent_payments, many=True)
        data = serializer.data
        
        # Manually enrich with student and fee info since nested serializers might not be present
        for i, payment_obj in enumerate(recent_payments):
            data[i]['student_name'] = payment_obj.student.user.get_full_name()
            data[i]['student_code'] = payment_obj.student.student_id
            data[i]['fee_title'] = payment_obj.fee.title
            
        return Response(data)
