import datetime
from django.utils import timezone
from rest_framework import status
from django.urls import reverse
from stsv_app.tests.base import BaseAPITestCase
from stsv_app.models.events import EventCategory, Event, CheckInSession, EventRegistration

class EventLifecycleAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.category = EventCategory.objects.first()
        
        # Tạo sẵn 1 sự kiện chưa duyệt
        self.pending_event = Event.objects.create(
            category=self.category,
            title="Sự kiện chờ duyệt",
            description="Mô tả sự kiện",
            location="Hội trường",
            start_time=timezone.now() + datetime.timedelta(days=1),
            end_time=timezone.now() + datetime.timedelta(days=2),
            organizer=self.org_officer,
            status=Event.Status.PENDING,
            max_participants=100
        )

        # Tạo sẵn 1 sự kiện đã duyệt để test đăng ký
        self.approved_event = Event.objects.create(
            category=self.category,
            title="Sự kiện đã duyệt",
            description="Mô tả sự kiện",
            location="Sân bóng",
            start_time=timezone.now() + datetime.timedelta(days=5),
            end_time=timezone.now() + datetime.timedelta(days=6),
            organizer=self.org_officer,
            status=Event.Status.APPROVED,
            max_participants=50
        )

    def test_org_officer_create_event(self):
        url = reverse('stsv_app:event-list')
        self.client.force_authenticate(user=self.org_officer)
        data = {
            "category": self.category.id,
            "title": "Sự kiện mới tạo",
            "description": "Chi tiết",
            "location": "A1-101",
            "start_time": (timezone.now() + datetime.timedelta(days=10)).isoformat(),
            "end_time": (timezone.now() + datetime.timedelta(days=11)).isoformat(),
            "max_participants": 200,
            "participation_points": 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_approve_event(self):
        url = reverse('stsv_app:event-approve', kwargs={'pk': self.pending_event.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_event.refresh_from_db()
        self.assertEqual(self.pending_event.status, Event.Status.APPROVED)

    def test_admin_reject_event(self):
        # Tạo thêm 1 event để reject
        event_to_reject = Event.objects.create(
            category=self.category, title="To reject", organizer=self.org_officer,
            start_time=timezone.now(), end_time=timezone.now() + datetime.timedelta(days=1),
            status=Event.Status.PENDING, max_participants=10
        )
        url = reverse('stsv_app:event-reject', kwargs={'pk': event_to_reject.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, {"reason": "Không hợp lệ"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event_to_reject.refresh_from_db()
        self.assertEqual(event_to_reject.status, Event.Status.REJECTED)

    def test_student_get_suggestions(self):
        url = reverse('stsv_app:event-suggestions')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_register_and_cancel_event(self):
        url_register = reverse('stsv_app:event-register', kwargs={'pk': self.approved_event.pk})
        url_cancel = reverse('stsv_app:event-cancel-registration', kwargs={'pk': self.approved_event.pk})
        
        self.client.force_authenticate(user=self.student)
        
        # Đăng ký
        res_reg = self.client.post(url_register)
        self.assertEqual(res_reg.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EventRegistration.objects.filter(event=self.approved_event, student=self.student.student_profile).exists())

        # Hủy đăng ký
        res_cancel = self.client.delete(url_cancel)
        self.assertEqual(res_cancel.status_code, status.HTTP_204_NO_CONTENT)
        # Service sẽ đổi status thành CANCELLED chứ ko xóa record
        reg = EventRegistration.objects.get(event=self.approved_event, student=self.student.student_profile)
        self.assertEqual(reg.status, EventRegistration.Status.CANCELLED)

    def test_full_checkin_flow(self):
        # 1. Sinh viên đăng ký
        EventRegistration.objects.create(
            event=self.approved_event,
            student=self.student.student_profile,
            status=EventRegistration.Status.REGISTERED
        )
        
        # 2. Tổ chức tạo phiên điểm danh (CheckInSession)
        url_session = reverse('stsv_app:event-sessions', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        res_session = self.client.post(url_session, {})
        self.assertEqual(res_session.status_code, status.HTTP_201_CREATED)
        
        dynamic_code = res_session.data.get('dynamic_code')
        
        # Để điểm danh được, sự kiện phải đang diễn ra
        self.approved_event.start_time = timezone.now() - datetime.timedelta(minutes=30)
        self.approved_event.save()

        # 3. Sinh viên điểm danh
        url_checkin = reverse('stsv_app:event-check-in', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        res_checkin = self.client.post(url_checkin, {"dynamic_code": dynamic_code})
        self.assertEqual(res_checkin.status_code, status.HTTP_200_OK, res_checkin.data)

    def test_event_statistics(self):
        url = reverse('stsv_app:event-statistics', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_registered', response.data)

    def test_send_reminder(self):
        url = reverse('stsv_app:event-send-reminder', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        data = {
            "title": "Nhắc nhở sự kiện",
            "message": "Ngày mai sự kiện bắt đầu nhé!",
            "target_group": "REGISTERED"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_youth_union_records(self):
        url = reverse('stsv_app:youth-union-record-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
