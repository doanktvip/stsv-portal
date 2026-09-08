from rest_framework import serializers
from stsv_app.models import FeeCampaign, Payment


class FeeCampaignSerializer(serializers.ModelSerializer):
    vietqr_url = serializers.SerializerMethodField()
    paid_count = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    my_payment_status = serializers.SerializerMethodField()
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)
    homeroom_class_name = serializers.CharField(source='homeroom_class.name', read_only=True)

    class Meta:
        model = FeeCampaign
        fields = [
            'id', 'title', 'description', 'amount', 'is_mandatory',
            'bank_name', 'bank_account_number', 'bank_account_name',
            'due_date', 'created_at', 'vietqr_url', 'paid_count', 
            'total_students', 'my_payment_status', 'creator_name', 'homeroom_class_name'
        ]

    def get_vietqr_url(self, obj):
        if not hasattr(obj, 'get_vietqr_url'):
            return ""
        request = self.context.get('request')
        student_code = "SV"
        if request and request.user.is_authenticated and hasattr(request.user, 'student_profile'):
            student_code = request.user.student_profile.student_id
        return obj.get_vietqr_url(student_code=student_code)

    def get_paid_count(self, obj):
        if hasattr(obj, 'paid_count_annotated'):
            return obj.paid_count_annotated
        if hasattr(obj, 'payments'):
            return obj.payments.filter(status=Payment.Status.SUCCESS).count()
        return 0

    def get_total_students(self, obj):
        if hasattr(obj, 'total_students_annotated'):
            return obj.total_students_annotated
        if hasattr(obj, 'homeroom_class') and obj.homeroom_class:
            return obj.homeroom_class.students.count()
        return 0

    def get_my_payment_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(request.user, 'student_profile'):
            prefetched = getattr(obj, '_prefetched_user_payments', None)
            if prefetched is not None:
                payment = prefetched[0] if prefetched else None
            elif hasattr(obj, 'payments'):
                payment = obj.payments.filter(student=request.user.student_profile).first()
            else:
                payment = None
            if payment:
                return {
                    'payment_id': payment.id,
                    'status': payment.status,
                    'payment_method': payment.payment_method,
                    'paid_at': payment.paid_at,
                }
        return None


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_id', read_only=True)
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'campaign', 'campaign_title', 'student', 'student_name', 
            'student_code', 'amount', 'payment_method', 'status', 
            'transaction_id', 'notes', 'paid_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['campaign', 'amount', 'payment_method', 'notes']


class ConfirmPaymentSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[Payment.Status.SUCCESS, Payment.Status.PENDING])
    notes = serializers.CharField(required=False, allow_blank=True, default='')
