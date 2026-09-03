from rest_framework import serializers
from stsv_app.models.support import Complaint, FacilityReport
from stsv_app.serializers.users import UserSerializer

class ComplaintSerializer(serializers.ModelSerializer):
    reporter_detail = UserSerializer(source='reporter', read_only=True)
    resolved_by_detail = UserSerializer(source='resolved_by', read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'reporter', 'reporter_detail', 'title', 'description', 'priority', 'status', 'resolved_by', 'resolved_by_detail', 'admin_response', 'created_at']
        read_only_fields = ['id', 'reporter', 'status', 'resolved_by', 'admin_response', 'created_at']


class FacilityReportSerializer(serializers.ModelSerializer):
    reporter_detail = UserSerializer(source='reporter', read_only=True)
    resolved_by_detail = UserSerializer(source='resolved_by', read_only=True)

    class Meta:
        model = FacilityReport
        fields = ['id', 'reporter', 'reporter_detail', 'room', 'description', 'image', 'priority', 'status', 'resolved_by', 'resolved_by_detail', 'resolution_image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reporter', 'status', 'resolved_by', 'resolution_image', 'created_at', 'updated_at']
