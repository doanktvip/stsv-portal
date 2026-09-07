from rest_framework import serializers
from stsv_app.models import Semester

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'code', 'start_date', 'end_date', 'is_evaluation_open']
