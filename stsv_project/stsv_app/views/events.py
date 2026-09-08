from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, permissions, filters, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from stsv_app.models import EventCategory, Event, CheckInSession
from stsv_app.serializers import EventCategorySerializer, EventSerializer, EventCreateSerializer,CheckInSessionSerializer, EventRegistrationSerializer, CheckInRequestSerializer
from rest_framework import serializers
from stsv_app.permissions import IsStudentRole, IsOrgOfficerRole, IsAdminRole
from stsv_app.services import EventService, ValidationError


class EventCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']


class EventViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'description', 'location']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = EventService()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateSerializer
        if self.action == 'check_in':
            return CheckInRequestSerializer
        if self.action == 'sessions':
            return CheckInSessionSerializer
        if self.action in ['register', 'cancel_registration']:
            return serializers.Serializer
        return EventSerializer  # pragma: no cover

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsOrgOfficerRole()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.service.user = request.user
        event = self.service.create_event(serializer.validated_data)
        
        return Response(EventSerializer(event, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        self.service.user = request.user
        try:
            event = self.service.update_event(instance, serializer.validated_data)
            return Response(EventSerializer(event, context={'request': request}).data)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super().get_queryset()
        self.service.user = self.request.user
        reg_status = self.request.query_params.get('registration_status')
        return self.service.get_events_for_user(qs, reg_status=reg_status)
        
    @action(detail=True, methods=['post'], permission_classes=[IsStudentRole])
    def register(self, request, pk=None):
        event = self.get_object()
        self.service.user = request.user
        try:
            reg = self.service.register_event(event)
            return Response(EventRegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsStudentRole])
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        self.service.user = request.user
        try:
            self.service.cancel_registration(event)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsStudentRole], url_path='check-in')
    def check_in(self, request, pk=None):
        event = self.get_object()
        dynamic_code = request.data.get('dynamic_code')
        self.service.user = request.user
        
        try:
            self.service.check_in(event, dynamic_code)
            return Response({"detail": "Điểm danh thành công."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsOrgOfficerRole])
    def sessions(self, request, pk=None):
        event = self.get_object()
        
        if request.method == 'GET':
            sessions = CheckInSession.objects.filter(event=event)
            return Response(CheckInSessionSerializer(sessions, many=True).data)
            
        elif request.method == 'POST':
            serializer = CheckInSessionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(event=event)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # pragma: no cover

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def approve(self, request, pk=None):
        event = self.get_object()
        self.service.user = request.user
        try:
            self.service.approve_event(event)
            return Response({"detail": "Sự kiện đã được duyệt thành công."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def reject(self, request, pk=None):
        event = self.get_object()
        reason = request.data.get('reason')
        self.service.user = request.user
        try:
            self.service.reject_event(event, reason)
            return Response({"detail": "Sự kiện đã bị từ chối."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def statistics(self, request, pk=None):
        event = self.get_object()
        self.service.user = request.user
        try:
            stats = self.service.get_event_statistics(event)
            return Response(stats, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_reminder(self, request, pk=None):
        event = self.get_object()
        title = request.data.get('title')
        message = request.data.get('message')
        target_group = request.data.get('target_group', 'REGISTERED')
        
        self.service.user = request.user
        try:
            count = self.service.send_event_reminder(event, title, message, target_group)
            return Response({"detail": f"Đã gửi thông báo thành công tới {count} sinh viên."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


