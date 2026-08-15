from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from stsv_app.models.finance import Fee, Payment
from stsv_app.serializers.finance import FeeSerializer, PaymentSerializer, PaymentCreateSerializer
from stsv_app.permissions import IsStudentRole


class FeeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FeeSerializer
    permission_classes = [IsStudentRole]

    def get_queryset(self):
        return Fee.objects.all()


class PaymentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsStudentRole]

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'studentprofile'):
            return Payment.objects.filter(student=self.request.user.studentprofile, is_deleted=False)
        return Payment.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        student_profile = self.request.user.studentprofile
        serializer.save(student=student_profile)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data['payment_url'] = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?..."
        return response

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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def webhook(self, request):
        # TODO: Verify webhook signature and update payment status
        # payload = request.data
        return Response({"detail": "Webhook received."}, status=status.HTTP_200_OK)
