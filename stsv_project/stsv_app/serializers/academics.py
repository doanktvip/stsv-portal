from rest_framework import serializers
from stsv_app.models.academics import EducationProgram, Subject, Semester, CourseClass, StudentCourse, Schedule, StudentSemesterSummary

class PrerequisiteSubjectSerializer(serializers.ModelSerializer):
    """Serializer lồng (nested) để hiển thị thông tin rút gọn của môn tiên quyết"""
    class Meta:
        model = Subject
        fields = ['id', 'subject_code', 'name']

class SubjectSerializer(serializers.ModelSerializer):
    # Dùng Serializer lồng nhau để trả ra mảng object thay vì mảng các ID
    prerequisite_subjects = PrerequisiteSubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'subject_code', 'name', 'credits', 'faculty', 'prerequisite_subjects']

class EducationProgramSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    credits = serializers.IntegerField(source='subject.credits', read_only=True)

    class Meta:
        model = EducationProgram
        fields = ['id', 'subject_code', 'subject_name', 'credits', 'recommended_semester', 'is_mandatory']

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'code', 'start_date', 'end_date']

class CourseClassSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    semester_code = serializers.CharField(source='semester.code', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.user.get_full_name', read_only=True, default=None)

    class Meta:
        model = CourseClass
        fields = [
            'id', 'subject', 'subject_code', 'subject_name', 
            'semester', 'semester_code', 
            'lecturer', 'lecturer_name', 
            'class_code', 'capacity', 'current_enrollment'
        ]
        read_only_fields = ['current_enrollment']

class StudentCourseSerializer(serializers.ModelSerializer):
    class_code = serializers.CharField(source='course_class.class_code', read_only=True)
    subject_name = serializers.CharField(source='course_class.subject.name', read_only=True)
    subject_code = serializers.CharField(source='course_class.subject.subject_code', read_only=True)
    semester_code = serializers.CharField(source='course_class.semester.code', read_only=True)
    credits = serializers.IntegerField(source='course_class.subject.credits', read_only=True)

    class Meta:
        model = StudentCourse
        fields = [
            'id', 'course_class', 'class_code', 'subject_name', 'subject_code', 'semester_code', 'credits',
            'total_score_10', 'total_score_4', 'total_score_letter', 'is_passed'
        ]
        read_only_fields = ['total_score_10', 'total_score_4', 'total_score_letter', 'is_passed']

class ScheduleSerializer(serializers.ModelSerializer):
    class_code = serializers.CharField(source='course_class.class_code', read_only=True)
    subject_name = serializers.CharField(source='course_class.subject.name', read_only=True)
    subject_code = serializers.CharField(source='course_class.subject.subject_code', read_only=True)
    semester_code = serializers.CharField(source='course_class.semester.code', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 'course_class', 'class_code', 'subject_name', 'subject_code', 'semester_code',
            'type', 'type_display', 'day_of_week', 'exact_date', 'start_time', 'end_time', 
            'room', 'is_makeup_class'
        ]

class StudentSemesterSummarySerializer(serializers.ModelSerializer):
    semester_code = serializers.CharField(source='semester.code', read_only=True)

    class Meta:
        model = StudentSemesterSummary
        fields = [
            'id', 'semester', 'semester_code', 
            'semester_gpa_4', 'semester_earned_credits', 'semester_training_points', 'training_point_classification',
            'cumulative_gpa_4', 'cumulative_earned_credits', 'cumulative_training_points'
        ]
