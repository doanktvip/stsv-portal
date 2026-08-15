from rest_framework import serializers
from stsv_app.models import EventCategory, Event, CheckInSession, EventRegistration, YouthUnionRecord
from stsv_app.serializers.users import UserSerializer

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name']

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['status', 'approved_by']

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['status', 'approved_by', 'organizer']

class CheckInRequestSerializer(serializers.Serializer):
    dynamic_code = serializers.CharField(max_length=255)

class CheckInSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInSession
        fields = '__all__'
        read_only_fields = ['event']

class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['student', 'status', 'queue_position', 'is_checked_in', 'check_in_time', 'check_out_time', 'feedback_submitted', 'registered_at']

class YouthUnionRecordSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True, default=None)

    class Meta:
        model = YouthUnionRecord
        fields = '__all__'