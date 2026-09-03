from django.utils import timezone
from rest_framework import viewsets, mixins, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from stsv_app.paginations import MasterDataPaginator
from stsv_app.permissions import IsStudentRole, IsAdminRole, IsLecturerRole
from stsv_app.models.academics import EducationProgram, Subject, Semester
from stsv_app.models.users import User
from stsv_app.serializers.academics import EducationProgramSerializer, SubjectSerializer, SemesterSerializer, CourseClassSerializer, StudentCourseSerializer, ScheduleSerializer, StudentSemesterSummarySerializer
from stsv_app.services.academics import SemesterService, SubjectService, EducationProgramService, CourseClassService, StudentCourseService, ScheduleService, StudentSemesterSummaryService


class StudentEducationProgramViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsStudentRole]
    serializer_class = EducationProgramSerializer

    def get_queryset(self):
        student_profile = self.request.user.student_profile
        service = EducationProgramService()
        return service.get_programs_for_student(student_profile)


class SubjectViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SubjectSerializer
    pagination_class = MasterDataPaginator
    permission_classes = [IsAdminRole | IsLecturerRole]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["faculty", "subject_code"]
    search_fields = ["subject_code", "name"]
    ordering_fields = ["id", "subject_code", "name", "credits"]

    def get_queryset(self):
        service = SubjectService()
        return service.get_subjects_for_user(self.request.user)


class SemesterViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code"]
    ordering_fields = ["id", "start_date"]

    def get_queryset(self):
        service = SemesterService()
        return service.get_semesters_for_user(self.request.user)

class CourseClassViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CourseClassSerializer
    permission_classes = [IsStudentRole | IsLecturerRole | IsAdminRole]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["subject", "semester"]
    search_fields = ["class_code", "subject__name"]
    ordering_fields = ["id", "class_code"]

    def get_queryset(self):
        service = CourseClassService()
        return service.get_course_classes(self.request.user)

class StudentCourseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = StudentCourseSerializer
    permission_classes = [IsStudentRole]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["course_class__semester"]
    search_fields = ["course_class__class_code", "course_class__subject__name"]

    def get_queryset(self):
        service = StudentCourseService()
        return service.get_my_courses(self.request.user)

class ScheduleViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsStudentRole | IsLecturerRole]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["course_class__semester", "exact_date", "type"]
    search_fields = ["course_class__class_code", "course_class__subject__name"]
    ordering_fields = ["exact_date", "start_time"]

    def get_queryset(self):
        service = ScheduleService()
        return service.get_personal_schedules(self.request.user)

class StudentSemesterSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = StudentSemesterSummarySerializer
    permission_classes = [IsStudentRole]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["semester"]

    def get_queryset(self):
        service = StudentSemesterSummaryService()
        return service.get_my_summaries(self.request.user)
