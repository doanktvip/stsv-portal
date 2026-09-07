from rest_framework import viewsets, mixins, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from stsv_app.paginations import MasterDataPaginator
from stsv_app.models import Faculty
from stsv_app.serializers import FacultySerializer

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


