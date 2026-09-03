from rest_framework import serializers
from stsv_app.models.core import Faculty, Major, Cohort

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'code', 'name']

class MajorSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    faculty_code = serializers.CharField(source='faculty.code', read_only=True)

    class Meta:
        model = Major
        fields = ['id', 'code', 'name', 'faculty', 'faculty_code', 'faculty_name']

class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = ['id', 'code', 'enrollment_year']
