from rest_framework import viewsets, mixins, permissions, filters
from stsv_app.serializers import SemesterSerializer
from stsv_app.services import SemesterService

class SemesterViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code"]
    ordering_fields = ["id", "start_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = SemesterService()

    def get_queryset(self):
        return self.service.get_semesters_for_user(self.request.user)

