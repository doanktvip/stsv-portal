from django.utils import timezone
from .base import BaseService
from stsv_app.models import Event, EventRegistration, CheckInSession, User, NotificationTemplate, UserNotification
from .exceptions import ValidationError

class EventService(BaseService):
    def get_events_for_user(self, base_qs, reg_status=None):
        if not self.user or self.user.is_anonymous:
            return base_qs.none()

        if self.user.role == User.Role.ADMIN:
            qs = base_qs

        elif self.user.role == User.Role.ORGOFFICER:
            if hasattr(self.user, 'org_profile'):
                qs = base_qs.filter(organizer=self.user.org_profile)
            else:
                qs = base_qs.none()


        else:
            qs = base_qs.filter(
                status=Event.Status.APPROVED,
                end_time__gte=timezone.now()
            )
            
        if reg_status and hasattr(self.user, 'student_profile'):
            student = self.user.student_profile  # pragma: no cover
            registered_event_ids = EventRegistration.objects.filter(  # pragma: no cover
                student=student,  # pragma: no cover
                status__in=[EventRegistration.Status.REGISTERED, EventRegistration.Status.WAITLIST, EventRegistration.Status.CHECKED_IN]  # pragma: no cover
            ).values_list('event_id', flat=True)  # pragma: no cover
              # pragma: no cover
            if reg_status == 'REGISTERED':  # pragma: no cover
                qs = qs.filter(id__in=registered_event_ids)  # pragma: no cover
            elif reg_status == 'UNREGISTERED':  # pragma: no cover
                qs = qs.exclude(id__in=registered_event_ids)  # pragma: no cover
                
        return qs

    @BaseService.run_in_transaction
    def create_event(self, event_data):
        event_data['organizer'] = self.user.org_profile
        
        status = event_data.get('status', Event.Status.DRAFT)
        if status not in [Event.Status.DRAFT, Event.Status.PENDING]:
            status = Event.Status.DRAFT
        event_data['status'] = status
        
        event = Event.objects.create(**event_data)
        
        if status == Event.Status.PENDING:
            self._notify_admins_new_event(event)
            
        return event

    @BaseService.run_in_transaction
    def update_event(self, event, event_data):
        if event.status in [Event.Status.PENDING, Event.Status.APPROVED]:
            raise ValidationError("Không thể chỉnh sửa sự kiện đang chờ duyệt hoặc đã duyệt.")
            
        new_status = event_data.get('status', event.status)
        if new_status not in [Event.Status.DRAFT, Event.Status.PENDING]:
            new_status = event.status
            
        event_data['status'] = new_status
        
        # Tránh ghi đè các trường nhạy cảm
        event_data.pop('organizer', None)
        event_data.pop('approved_by', None)
        
        for key, value in event_data.items():
            setattr(event, key, value)
            
        event.save()
        
        if new_status == Event.Status.PENDING:
            self._notify_admins_new_event(event)
            
        return event

    @BaseService.run_in_transaction
    def approve_event(self, event):
        if self.user.role != User.Role.ADMIN:
            raise ValidationError("Bạn không có quyền duyệt sự kiện này.")
        
        if event.status != Event.Status.PENDING:
            raise ValidationError("Chỉ có thể duyệt sự kiện đang chờ duyệt.")
            
        event.status = Event.Status.APPROVED
        event.approved_by = self.user
        event.save(update_fields=['status', 'approved_by'])
        
        self._notify_organizer_approval_result(event, approved=True)
        return event

    @BaseService.run_in_transaction
    def reject_event(self, event, reason):
        if self.user.role != User.Role.ADMIN:
            raise ValidationError("Bạn không có quyền từ chối sự kiện này.")
        
        if event.status != Event.Status.PENDING:
            raise ValidationError("Chỉ có thể từ chối sự kiện đang chờ duyệt.")
            
        if not reason:
            raise ValidationError("Vui lòng cung cấp lý do từ chối.")
            
        event.status = Event.Status.REJECTED
        event.approved_by = self.user
        event.save(update_fields=['status', 'approved_by'])
        
        self._notify_organizer_approval_result(event, approved=False, reason=reason)
        return event

    def _notify_organizer_approval_result(self, event, approved, reason=None):
        title = "Sự kiện đã được duyệt" if approved else "Sự kiện bị từ chối"
        message = f"Sự kiện '{event.title}' của bạn đã được duyệt." if approved else f"Sự kiện '{event.title}' của bạn đã bị từ chối. Lý do: {reason}"
        
        template = NotificationTemplate.objects.create(
            sender=self.user,
            title=title,
            message=message,
            type=NotificationTemplate.Type.EVENT,
            action_data={"event_id": event.id}
        )
        
        UserNotification.objects.create(user=event.organizer.user, template=template)

    def _notify_admins_new_event(self, event):
        admins = User.objects.filter(role=User.Role.ADMIN)
        if not admins.exists():
            return
            
        # Tạo Notification Content (dùng chung Template)
        template = NotificationTemplate.objects.create(
            sender=self.user,
            title="Sự kiện mới chờ duyệt",
            message=f"Ban tổ chức {self.user.get_full_name()} vừa đề xuất sự kiện '{event.title}'.",
            type=NotificationTemplate.Type.EVENT,
            action_data={"event_id": event.id}
        )
        
        # Phát thông báo cho tất cả Admin
        notifications = [
            UserNotification(user=admin, template=template)
            for admin in admins
        ]
        UserNotification.objects.bulk_create(notifications)

    @BaseService.run_in_transaction
    def register_event(self, event):
        locked_event = Event.objects.select_for_update().get(id=event.id)
        
        if locked_event.status != Event.Status.APPROVED:
            raise ValidationError("Chỉ có thể đăng ký sự kiện đã được duyệt.")
        
        student = self.user.student_profile
        
        current_participants = EventRegistration.objects.filter(
            event=locked_event, status=EventRegistration.Status.REGISTERED
        ).count()
        
        reg_status = EventRegistration.Status.REGISTERED
        
        if current_participants >= locked_event.capacity:
            current_waitlist = EventRegistration.objects.filter(
                event=locked_event, status=EventRegistration.Status.WAITLIST
            ).count()
            if current_waitlist >= locked_event.waitlist_capacity:
                raise ValidationError("Sự kiện đã đầy và danh sách chờ đã đầy.")
            reg_status = EventRegistration.Status.WAITLIST
        else:
            # Check overlapping events only if registering (not waitlist)
            overlapping_events = EventRegistration.objects.filter(
                student=student,
                status=EventRegistration.Status.REGISTERED,
                event__start_time__lt=locked_event.end_time,
                event__end_time__gt=locked_event.start_time
            ).exists()

            if overlapping_events:
                raise ValidationError("Không thể đăng ký do trùng lịch học hoặc sự kiện khác.")
                
        reg = EventRegistration.objects.filter(event=locked_event, student=student).first()
        if reg:
            if reg.status in [EventRegistration.Status.REGISTERED, EventRegistration.Status.WAITLIST, EventRegistration.Status.CHECKED_IN]:
                raise ValidationError("Bạn đã đăng ký sự kiện này.")
            reg.status = reg_status
            reg.save(update_fields=['status'])
        else:
            reg = EventRegistration.objects.create(
                event=locked_event,
                student=student,
                status=reg_status
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
            
            reg.delete()
            
            if was_registered:
                next_in_queue = EventRegistration.objects.filter(
                    event=locked_event, 
                    status=EventRegistration.Status.WAITLIST
                ).order_by('registered_at').first()
                
                if next_in_queue:
                    next_in_queue.status = EventRegistration.Status.REGISTERED
                    next_in_queue.save(update_fields=['status'])
                    
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
            reg.status = EventRegistration.Status.CHECKED_IN
            reg.save(update_fields=['status'])
            
            return reg
        except EventRegistration.DoesNotExist:
            raise ValidationError("Không tìm thấy thông tin đăng ký hoặc bạn đã điểm danh.")

    def get_event_statistics(self, event):
        if self.user.role not in [User.Role.ADMIN, User.Role.ORGOFFICER]:
            raise ValidationError("Bạn không có quyền xem thống kê sự kiện này.")
            
        if self.user.role == User.Role.ORGOFFICER and event.organizer != self.user.org_profile:
            raise ValidationError("Bạn chỉ được xem thống kê sự kiện do mình tổ chức.")  # pragma: no cover

        total_registered = EventRegistration.objects.filter(
            event=event, status=EventRegistration.Status.REGISTERED
        ).count()
        
        total_waitlist = EventRegistration.objects.filter(
            event=event, status=EventRegistration.Status.WAITLIST
        ).count()
        
        total_checked_in = EventRegistration.objects.filter(
            event=event, status=EventRegistration.Status.CHECKED_IN
        ).count()
        
        return {
            "max_participants": event.capacity,
            "waiting_list_capacity": event.waitlist_capacity,
            "total_registered": total_registered,
            "total_waitlist": total_waitlist,
            "total_checked_in": total_checked_in,
        }

    def send_event_reminder(self, event, title, message, target_group="REGISTERED"):
        if self.user.role not in [User.Role.ADMIN, User.Role.ORGOFFICER]:
            raise ValidationError("Bạn không có quyền gửi nhắc nhở cho sự kiện này.")
            
        if self.user.role == User.Role.ORGOFFICER and event.organizer != self.user.org_profile:
            raise ValidationError("Bạn chỉ được gửi nhắc nhở cho sự kiện do mình tổ chức.")  # pragma: no cover

        if not title or not message:
            raise ValidationError("Tiêu đề và nội dung không được để trống.")

        # Lọc danh sách sinh viên theo target_group
        regs = EventRegistration.objects.filter(event=event)
        if target_group == "REGISTERED":
            regs = regs.filter(status=EventRegistration.Status.REGISTERED)
        elif target_group == "WAITLIST":
            regs = regs.filter(status=EventRegistration.Status.WAITLIST)
        elif target_group == "CHECKED_IN":
            regs = regs.filter(status=EventRegistration.Status.CHECKED_IN)
        elif target_group == "ALL":
            regs = regs.filter(status__in=[EventRegistration.Status.REGISTERED, EventRegistration.Status.WAITLIST])
        else:
            raise ValidationError("Nhóm đối tượng không hợp lệ.")

        students = [reg.student.user for reg in regs.select_related('student__user')]
        if not students:
            return 0

        template = NotificationTemplate.objects.create(
            sender=self.user,
            title=title,
            message=message,
            type=NotificationTemplate.Type.REMINDER,
            action_data={"event_id": event.id}
        )
        
        notifications = [
            UserNotification(user=student, template=template)
            for student in students
        ]
        UserNotification.objects.bulk_create(notifications)
        
        return len(students)

