from rest_framework import serializers
from stsv_app.models import StudentSemesterPoint, PointTransaction, TrainingRule

class StudentSemesterPointSerializer(serializers.ModelSerializer):
    is_evaluation_open = serializers.SerializerMethodField()
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)

    class Meta:
        model = StudentSemesterPoint
        fields = '__all__'

    def get_is_evaluation_open(self, obj):
        return obj.semester.is_evaluation_open

class TrainingRuleSerializer(serializers.ModelSerializer):
    criterion_name = serializers.CharField(source='criterion.name', read_only=True)
    max_points = serializers.IntegerField(source='criterion.max_points', read_only=True)
    
    class Meta:
        model = TrainingRule
        fields = '__all__'

class PointTransactionSerializer(serializers.ModelSerializer):
    criterion_code = serializers.SerializerMethodField()

    class Meta:
        model = PointTransaction
        fields = '__all__'
        read_only_fields = ['student', 'semester', 'status', 'event']

    def get_criterion_code(self, obj):
        if obj.event and obj.event.category and obj.event.category.criterion:
            return obj.event.category.criterion.name
        elif obj.rule and obj.rule.criterion:
            return obj.rule.criterion.name
        return "Khác"
