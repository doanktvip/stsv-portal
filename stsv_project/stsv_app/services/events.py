from .base import BaseService
from stsv_app.models.events import Event, EventRegistration, CheckInSession
from .exceptions import ResourceNotFoundError, ValidationError
from django.utils import timezone

class EventService(BaseService):
    def get_event_details(self, event_id: int) -> Event:
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy sự kiện.")

    @BaseService.run_in_transaction
    def register_for_event(self, student_profile_id: int, event_id: int) -> EventRegistration:
        event = self.get_event_details(event_id)
        
        if event.status != Event.Status.APPROVED:
            raise ValidationError("Sự kiện chưa được mở đăng ký.")
            
        if event.max_participants > 0 and EventRegistration.objects.filter(event_id=event_id, status=EventRegistration.Status.REGISTERED).count() >= event.max_participants:
            raise ValidationError("Sự kiện đã đủ số lượng người tham gia.")
            
        if EventRegistration.objects.filter(student_id=student_profile_id, event_id=event_id).exists():
            raise ValidationError("Sinh viên đã đăng ký sự kiện này rồi.")
            
        registration = EventRegistration(
            student_id=student_profile_id, 
            event_id=event_id,
            status=EventRegistration.Status.REGISTERED
        )
        registration.save()
        return registration

    def check_in_event(self, registration_id: int) -> EventRegistration:
        try:
            registration = EventRegistration.objects.get(id=registration_id)
        except EventRegistration.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy thông tin đăng ký.")
            
        if registration.status != EventRegistration.Status.REGISTERED:
            raise ValidationError("Đăng ký không hợp lệ.")
            
        if registration.is_checked_in:
            raise ValidationError("Sinh viên đã check-in sự kiện này rồi.")
            
        registration.is_checked_in = True
        registration.check_in_time = timezone.now()
        registration.save()
            
        return registration
