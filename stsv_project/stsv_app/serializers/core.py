from rest_framework import serializers
from stsv_app.models import Faculty

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'code', 'name']
