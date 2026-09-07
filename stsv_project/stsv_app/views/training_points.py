from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from stsv_app.permissions import IsStudentOrBanCanSuRole, IsClassPresident, IsOrgOfficerRole
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from stsv_app.services import TrainingPointService
from stsv_app.models import StudentSemesterPoint, PointTransaction, TrainingRule
from stsv_app.serializers import StudentSemesterPointSerializer, PointTransactionSerializer, TrainingRuleSerializer

class TrainingRuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainingRule.objects.all().order_by('id')
    serializer_class = TrainingRuleSerializer
    permission_classes = [IsAuthenticated]


class StudentSemesterPointViewSet(viewsets.ModelViewSet):
    queryset = StudentSemesterPoint.objects.all()
    serializer_class = StudentSemesterPointSerializer
    permission_classes = [IsStudentOrBanCanSuRole]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TrainingPointService()

    def get_queryset(self):
        user = self.request.user
        if user.role in [user.Role.STUDENT, user.Role.BANCANSU]:
            return self.queryset.filter(student__user=user)
        return self.queryset

    @action(detail=False, methods=['get'])
    def my_points(self, request):
        user = request.user
        self.service.user = user
        semester_id = request.query_params.get('semester_id')
        semester = self.service.get_active_semester(semester_id)
                
        if not semester:
            return Response({"detail": "Không tìm thấy học kỳ nào."}, status=404)
            
        try:
            point = self.service.calculate_student_points(semester)
            serializer = self.get_serializer(point)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        user = request.user
        self.service.user = user
        semester_id = request.data.get('semester_id')
        semester = self.service.get_active_semester(semester_id)
        
        if not semester:
            return Response({"detail": "Không tìm thấy học kỳ nào."}, status=404)
            
        try:
            points_data = request.data.get('points_data')
            total_student_score = request.data.get('total_student_score')
            is_draft = request.data.get('is_draft', False)
            
            point = self.service.submit_student_points(
                semester, 
                points_data=points_data, 
                total_student_score=total_student_score, 
                is_draft=is_draft
            )
            serializer = self.get_serializer(point)
            msg = "Đã lưu nháp bảng điểm thành công!" if is_draft else "Đã chốt điểm rèn luyện thành công!"
            return Response({"detail": msg, "data": serializer.data})
        except ValidationError as e: # pragma: no cover
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=False, methods=['get'], permission_classes=[IsClassPresident])
    def class_list(self, request):
        user = request.user
        self.service.user = user
        semester_id = request.query_params.get('semester_id')
        semester = self.service.get_active_semester(semester_id)
        
        if not semester:
            return Response({"detail": "Không tìm thấy học kỳ nào."}, status=404)
            
        try:
            class_name, points = self.service.get_class_points_list(semester)
            serializer = self.get_serializer(points, many=True)
            return Response({"class_name": class_name, "data": serializer.data})
        except ValidationError as e:
            return Response({"detail": str(e)}, status=403)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsClassPresident])
    def class_approve(self, request, pk=None):
        point = self.get_object()
        self.service.user = request.user
        
        try:
            total_class_score = request.data.get('total_class_score')
            class_points_data = request.data.get('class_points_data')
            is_draft = request.data.get('is_draft', False)
            point = self.service.approve_student_points_by_class(
                point, 
                total_class_score=total_class_score, 
                class_points_data=class_points_data, 
                is_draft=is_draft
            )
            serializer = self.get_serializer(point)
            msg = "Đã lưu nháp thành công!" if is_draft else "Đã duyệt điểm thành công!"
            return Response({"detail": msg, "data": serializer.data})
        except ValidationError as e: # pragma: no cover
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=False, methods=['post'], permission_classes=[IsOrgOfficerRole])
    def open_evaluation(self, request):
        self.service.user = request.user
        semester_id = request.data.get('semester_id')
        semester = self.service.get_active_semester(semester_id)
        if not semester:
            return Response({"detail": "Không tìm thấy học kỳ."}, status=404)
            
        try:
            self.service.open_evaluation(semester)
            return Response({"detail": "Đã mở đợt chấm điểm cho toàn trường!"})
        except ValidationError as e:
            return Response({"detail": str(e)}, status=403)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=False, methods=['get'], permission_classes=[IsOrgOfficerRole])
    def faculty_list(self, request):
        self.service.user = request.user
        semester = self.service.get_active_semester(request.query_params.get('semester_id'))
        
        if not semester:
            return Response({"detail": "Không tìm thấy học kỳ nào."}, status=404)
            
        try:
            class_id = request.query_params.get('class_id')
            data, is_points = self.service.get_faculty_points_list(semester, class_id)
            if is_points:
                serializer = self.get_serializer(data, many=True)  # pragma: no cover
                return Response({"data": serializer.data})  # pragma: no cover
            else:
                return Response({"data": data})
        except ValidationError as e:
            return Response({"detail": str(e)}, status=403)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsOrgOfficerRole])
    def faculty_approve(self, request, pk=None):
        point = self.get_object()
        self.service.user = request.user
        
        try:
            total_final_score = request.data.get('total_final_score')
            faculty_points_data = request.data.get('faculty_points_data')
            is_draft = request.data.get('is_draft', False)
            point = self.service.approve_student_points_by_faculty(
                point, 
                total_final_score=total_final_score,
                faculty_points_data=faculty_points_data,
                is_draft=is_draft
            )
            serializer = self.get_serializer(point)
            msg = "Đã lưu nháp thành công!" if is_draft else "Khoa đã duyệt điểm thành công!"
            return Response({"detail": msg, "data": serializer.data})
        except ValidationError as e: # pragma: no cover
            return Response({"detail": str(e)}, status=400)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class PointTransactionViewSet(viewsets.ModelViewSet):
    queryset = PointTransaction.objects.all()
    serializer_class = PointTransactionSerializer
    permission_classes = [IsStudentOrBanCanSuRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = TrainingPointService()

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        if user.role in [user.Role.STUDENT, user.Role.BANCANSU]:
            queryset = queryset.filter(student__user=user)
            
        semester_id = self.request.query_params.get('semester_id')
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        self.service.user = user
        current_semester = self.service.get_active_semester()
        
        if not current_semester:
            raise ValidationError("Hệ thống chưa có Học kỳ nào được cấu hình.")

        serializer.save(  # pragma: no cover
            student=user.student_profile,
            semester=current_semester,
            status=PointTransaction.Status.PENDING
        )

