from rest_framework import viewsets, mixins, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from stsv_app.paginations import MasterDataPaginator
from stsv_app.models.core import Faculty, Major, Cohort
from stsv_app.serializers.core import (
    FacultySerializer,
    MajorSerializer,
    CohortSerializer,
)


class FacultyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Faculty.objects.all().order_by("id")
    serializer_class = FacultySerializer
    pagination_class = MasterDataPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["code"]
    search_fields = ["code", "name"]
    ordering_fields = ["id", "code", "name"]


class MajorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Major.objects.select_related("faculty").all().order_by("id")
    serializer_class = MajorSerializer
    pagination_class = MasterDataPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["faculty", "code"]
    search_fields = ["code", "name"]
    ordering_fields = ["id", "code", "name"]


class CohortViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Cohort.objects.all().order_by("-enrollment_year", "id")
    serializer_class = CohortSerializer
    pagination_class = MasterDataPaginator
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["code", "enrollment_year"]
    search_fields = ["code"]
    ordering_fields = ["id", "code", "enrollment_year"]
