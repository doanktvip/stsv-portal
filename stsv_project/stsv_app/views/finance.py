from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stsv_app.models import Payment
from stsv_app.serializers import FeeCampaignSerializer, PaymentSerializer, PaymentCreateSerializer, ConfirmPaymentSerializer
from stsv_app.permissions import IsStudentOrBanCanSuRole
from stsv_app.services import FinanceService, ResourceNotFoundError, ValidationError


class FeeCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = FeeCampaignSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = FinanceService()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStudentOrBanCanSuRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return self.service.get_campaigns_for_user(self.request.user)

    def perform_create(self, serializer):
        campaign = self.service.create_fee_campaign(
            creator=self.request.user,
            validated_data=serializer.validated_data
        )
        serializer.instance = campaign


class PaymentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsStudentOrBanCanSuRole]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = FinanceService()

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student_profile'):
            return Payment.objects.filter(student=self.request.user.student_profile).order_by('-id')
        return Payment.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        campaign = serializer.validated_data['campaign']
        amount = serializer.validated_data.get('amount')
        payment_method = serializer.validated_data.get('payment_method', Payment.PaymentMethod.VIETQR)
        notes = serializer.validated_data.get('notes', '')

        try:
            result = self.service.initiate_payment(
                user=request.user,
                campaign_id=campaign.id,
                amount=amount,
                payment_method=payment_method,
                notes=notes
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except (ValidationError, ResourceNotFoundError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClassFinanceManagementViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = FinanceService()

    @action(detail=True, methods=['get'], url_path='class-status')
    def class_status(self, request, pk=None):
        try:
            result = self.service.get_class_finance_status(user=request.user, campaign_id=pk)
            return Response(result, status=status.HTTP_200_OK)
        except ResourceNotFoundError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='toggle-payment')
    def toggle_payment(self, request, pk=None):
        serializer = ConfirmPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')

        try:
            payment = self.service.toggle_payment_status(
                user=request.user,
                payment_id=pk,
                target_status=target_status,
                notes=notes
            )
            return Response({'detail': 'Cập nhật trạng thái thanh toán thành công', 'status': payment.status})
        except ResourceNotFoundError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='confirm-cash')
    def confirm_cash(self, request):
        campaign_id = request.data.get('campaign_id')
        student_id = request.data.get('student_id')

        try:
            payment = self.service.confirm_cash_payment(
                user=request.user,
                campaign_id=campaign_id,
                student_id=student_id
            )
            return Response({'detail': f'Đã xác nhận nộp tiền mặt thành công', 'status': payment.status})
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
