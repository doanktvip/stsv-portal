import uuid
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from stsv_app.models import EventCategory, Event, CheckInSession, EventRegistration
from stsv_app.serializers.users import OrgProfileSerializer

class EventCategorySerializer(serializers.ModelSerializer):
    criterion_name = serializers.CharField(source='criterion.name', read_only=True)
    
    class Meta:
        model = EventCategory
        fields = ['id', 'name', 'criterion_name']

class EventSerializer(serializers.ModelSerializer):
    organizer = OrgProfileSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    criterion_name = serializers.CharField(source='category.criterion.name', read_only=True)
    available_tickets = serializers.SerializerMethodField()
    available_waiting_list_seats = serializers.SerializerMethodField()
    user_registration_status = serializers.SerializerMethodField()
    event_state = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['status', 'approved_by']

    def get_event_state(self, obj):
        now = timezone.now()
        if now < obj.start_time:
            return "UPCOMING"
        elif obj.start_time <= now <= obj.end_time:
            return 'ONGOING'
        else:
            return 'CLOSED'

    def get_available_tickets(self, obj):
        registered_count = EventRegistration.objects.filter(
            event=obj, 
            status=EventRegistration.Status.REGISTERED
        ).count()
        return max(0, obj.capacity - registered_count)

    def get_available_waiting_list_seats(self, obj):
        waitlist_count = EventRegistration.objects.filter(
            event=obj, 
            status=EventRegistration.Status.WAITLIST
        ).count()
        return max(0, obj.waitlist_capacity - waitlist_count)

    def get_user_registration_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 'UNREGISTERED'
        
        if not hasattr(request.user, 'student_profile'):
            return 'UNREGISTERED'

        reg = EventRegistration.objects.filter(
            event=obj, 
            student=request.user.student_profile
        ).order_by('-registered_at').first()
        
        if reg:
            if reg.status == EventRegistration.Status.WAITLIST:
                return 'WAITING_LIST'
            return reg.status  # pragma: no cover
        return 'UNREGISTERED'  # pragma: no cover

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['approved_by', 'organizer']

class CheckInRequestSerializer(serializers.Serializer):
    dynamic_code = serializers.CharField(max_length=255)

class CheckInSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInSession
        fields = '__all__'
        read_only_fields = ['event', 'dynamic_code', 'expires_at']

    def create(self, validated_data):
        # Tự động sinh mã code và thời gian hết hạn (10 phút)
        validated_data['dynamic_code'] = str(uuid.uuid4())
        validated_data['expires_at'] = timezone.now() + timedelta(minutes=10)
        # Xóa toàn bộ các phiên điểm danh cũ của sự kiện này
        event = validated_data.get('event')
        if event:
            CheckInSession.objects.filter(event=event).delete()
            
        return super().create(validated_data)

class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['student', 'status', 'queue_position', 'is_checked_in', 'check_in_time', 'check_out_time', 'feedback_submitted', 'registered_at']

