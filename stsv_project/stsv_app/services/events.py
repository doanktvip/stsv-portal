from django.utils import timezone
from .base import BaseService
from stsv_app.models import Event, EventRegistration, CheckInSession, User, YouthUnionRecord
from .exceptions import ValidationError

class EventService(BaseService):
    def get_events_for_user(self, base_qs):
        if not self.user or self.user.is_anonymous:
            return base_qs.none()

        if self.user.role == User.Role.ADMIN:
            return base_qs

        elif self.user.role == User.Role.ORGOFFICER:
            return base_qs.filter(organizer=self.user)

        else:
            return base_qs.filter(status=Event.Status.APPROVED)

    @BaseService.run_in_transaction
    def create_event(self, event_data):
        event_data['organizer'] = self.user
        event_data['status'] = Event.Status.PENDING
        return Event.objects.create(**event_data)

    @BaseService.run_in_transaction
    def register_event(self, event):
        locked_event = Event.objects.select_for_update().get(id=event.id)
        
        student = self.user.student_profile
        
        if EventRegistration.objects.filter(
            event=locked_event, student=student, 
            status__in=[EventRegistration.Status.REGISTERED, EventRegistration.Status.WAITLIST]
        ).exists():
            raise ValidationError("Bạn đã đăng ký sự kiện này.")
            
        current_participants = EventRegistration.objects.filter(
            event=locked_event, status=EventRegistration.Status.REGISTERED
        ).count()
        
        reg_status = EventRegistration.Status.REGISTERED
        queue_position = 0
        
        if current_participants >= locked_event.max_participants:
            current_waitlist = EventRegistration.objects.filter(
                event=locked_event, status=EventRegistration.Status.WAITLIST
            ).count()
            if current_waitlist >= locked_event.waiting_list_capacity:
                raise ValidationError("Sự kiện đã đầy và danh sách chờ đã đầy.")
            reg_status = EventRegistration.Status.WAITLIST
            queue_position = current_waitlist + 1

        reg = EventRegistration.objects.create(
            event=locked_event,
            student=student,
            status=reg_status,
            queue_position=queue_position
        )
        return reg


    @BaseService.run_in_transaction
    def cancel_registration(self, event):
        locked_event = Event.objects.select_for_update().get(id=event.id)
        student = self.user.student_profile
        
        try:
            reg = EventRegistration.objects.get(
                event=locked_event, student=student, 
                status__in=[EventRegistration.Status.REGISTERED, EventRegistration.Status.WAITLIST]
            )
            
            was_registered = (reg.status == EventRegistration.Status.REGISTERED)
            
            reg.status = EventRegistration.Status.CANCELLED
            reg.save(update_fields=['status'])
            
            if was_registered:
                next_in_queue = EventRegistration.objects.filter(
                    event=locked_event, 
                    status=EventRegistration.Status.WAITLIST
                ).order_by('queue_position', 'registered_at').first()
                
                if next_in_queue:
                    next_in_queue.status = EventRegistration.Status.REGISTERED
                    next_in_queue.queue_position = 0
                    next_in_queue.save(update_fields=['status', 'queue_position'])
                    
            return reg
        except EventRegistration.DoesNotExist:
            raise ValidationError("Bạn chưa đăng ký sự kiện này.")

    @BaseService.run_in_transaction
    def check_in(self, event, dynamic_code):
        if not dynamic_code:
            raise ValidationError("Cần cung cấp dynamic_code.")
            
        student = self.user.student_profile
        
        try:
            session = CheckInSession.objects.get(event=event, dynamic_code=dynamic_code)
            if session.expires_at < timezone.now():
                raise ValidationError("Phiên điểm danh đã hết hạn.")
        except CheckInSession.DoesNotExist:
            raise ValidationError("Mã điểm danh không hợp lệ.")
            
        try:
            reg = EventRegistration.objects.select_for_update().get(
                event=event, student=student, 
                status=EventRegistration.Status.REGISTERED
            )
            if reg.is_checked_in:
                raise ValidationError("Bạn đã điểm danh rồi.")
                
            reg.is_checked_in = True
            reg.check_in_time = timezone.now()
            self._create_youth_union_record(student, event, reg.check_in_time)
            reg.save(update_fields=['is_checked_in', 'check_in_time'])
            
            return reg
        except EventRegistration.DoesNotExist:
            raise ValidationError("Không tìm thấy thông tin đăng ký hoặc bạn đang ở danh sách chờ.")

    def _create_youth_union_record(self, student, event, check_in_time):
        if not event.is_youth_union:
            return
        
        # Kiểm tra xem đã có bản ghi chưa để tránh tạo trùng lặp
        if not YouthUnionRecord.objects.filter(student=student, event=event).exists():
            YouthUnionRecord.objects.create(
                student=student,
                activity_name=event.title,
                event=event,
                description=f"Điểm danh tham gia sự kiện lúc {check_in_time.strftime('%H:%M %d/%m/%Y')}",
                date=event.start_time.date(),
            )
