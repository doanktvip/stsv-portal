from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from stsv_app.models.support import Complaint, FacilityReport
from stsv_app.serializers.support import ComplaintSerializer, FacilityReportSerializer
from rest_framework.exceptions import PermissionDenied

class BaseSupportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.select_related('reporter', 'resolved_by')
        if user.role == "ADMIN":
            return qs
        return qs.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user, status="PENDING")

class ComplaintViewSet(BaseSupportViewSet):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority']

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve_complaint(self, request, pk=None):
        if request.user.role != "ADMIN":
            raise PermissionDenied("Chỉ Admin mới có quyền giải quyết khiếu nại.")
        
        complaint = self.get_object()
        admin_response = request.data.get('admin_response', '')
        
        if not admin_response.strip():
            return Response({"message": "Nội dung phản hồi không được để trống."}, status=status.HTTP_400_BAD_REQUEST)

        complaint.admin_response = admin_response
        complaint.status = "CLOSED"
        complaint.resolved_by = request.user
        complaint.save()
        
        return Response({"status": "success", "message": "Đã giải quyết khiếu nại thành công."})

class FacilityReportViewSet(BaseSupportViewSet):
    queryset = FacilityReport.objects.all().order_by('-created_at')
    serializer_class = FacilityReportSerializer
    filterset_fields = ['status', 'priority']
    search_fields = ['room', 'description']
    ordering_fields = ['created_at', 'priority']

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve_report(self, request, pk=None):
        if request.user.role != "ADMIN":
            raise PermissionDenied("Chỉ Admin mới có quyền giải quyết báo cáo.")
        
        report = self.get_object()
        
        # Nếu có gửi ảnh khắc phục
        resolution_image = request.FILES.get('resolution_image', None)
        if resolution_image:
            report.resolution_image = resolution_image
            
        report.status = "RESOLVED"
        report.resolved_by = request.user
        report.save()
        
        return Response({"status": "success", "message": "Đã ghi nhận khắc phục sự cố thành công."})
