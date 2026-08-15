from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from stsv_app.models import EventCategory, Event, CheckInSession, YouthUnionRecord
from stsv_app.serializers.events import (
    EventCategorySerializer, EventSerializer, EventCreateSerializer,
    CheckInSessionSerializer, EventRegistrationSerializer, YouthUnionRecordSerializer,
    CheckInRequestSerializer
)
from rest_framework import serializers
from stsv_app.permissions import IsStudentRole, IsOrgOfficerRole
from stsv_app.services.events import EventService
from stsv_app.services.exceptions import ValidationError


class EventCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'description', 'location']

    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        if self.action == 'check_in':
            return CheckInRequestSerializer
        if self.action == 'sessions':
            return CheckInSessionSerializer
        if self.action in ['register', 'cancel_registration']:
            return serializers.Serializer
        return EventSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsOrgOfficerRole()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = EventService(request.user)
        event = service.create_event(serializer.validated_data)
        
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = super().get_queryset()
        service = EventService(self.request.user)
        return service.get_events_for_user(qs)

    @action(detail=True, methods=['post'], permission_classes=[IsStudentRole])
    def register(self, request, pk=None):
        event = self.get_object()
        service = EventService(request.user)
        try:
            reg = service.register_event(event)
            return Response(EventRegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @register.mapping.delete
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        service = EventService(request.user)
        try:
            service.cancel_registration(event)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsStudentRole], url_path='check-in')
    def check_in(self, request, pk=None):
        event = self.get_object()
        dynamic_code = request.data.get('dynamic_code')
        service = EventService(request.user)
        
        try:
            service.check_in(event, dynamic_code)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YouthUnionRecordViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = YouthUnionRecordSerializer
    permission_classes = [IsStudentRole]
    
    def get_queryset(self):
        return YouthUnionRecord.objects.filter(student=self.request.user.student_profile)
