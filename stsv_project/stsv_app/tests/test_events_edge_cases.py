# Standard library
import datetime

# Django
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.utils import timezone

# Django REST Framework
from rest_framework import serializers, status

# App imports
from stsv_app.models.events import EventCategory, Event, EventRegistration, CheckInSession
from stsv_app.models.users import User, StudentProfile, OrgProfile
from stsv_app.serializers.events import CheckInRequestSerializer, CheckInSessionSerializer
from stsv_app.services.events import EventService
from stsv_app.tests.base import BaseAPITestCase
from stsv_app.views.events import EventViewSet


class EventEdgeCasesAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.category = EventCategory.objects.first()

        self.draft_event = Event.objects.create(
            category=self.category,
            title="Draft Event",
            description="Mô tả",
            location="HT A",
            start_time=timezone.now() + datetime.timedelta(days=1),
            end_time=timezone.now() + datetime.timedelta(days=2),
            organizer=self.org_officer,
            status=Event.Status.DRAFT,
            max_participants=1,
            waiting_list_capacity=1
        )

        self.pending_event = Event.objects.create(
            category=self.category,
            title="Pending Event",
            description="Mô tả",
            location="HT B",
            start_time=timezone.now() + datetime.timedelta(days=1),
            end_time=timezone.now() + datetime.timedelta(days=2),
            organizer=self.org_officer,
            status=Event.Status.PENDING,
            max_participants=1,
            waiting_list_capacity=1
        )

        self.approved_event = Event.objects.create(
            category=self.category,
            title="Approved Event",
            description="Mô tả",
            location="Sân bóng",
            start_time=timezone.now() + datetime.timedelta(days=5),
            end_time=timezone.now() + datetime.timedelta(days=6),
            organizer=self.org_officer,
            status=Event.Status.APPROVED,
            max_participants=1,
            waiting_list_capacity=1
        )

    # 1. Update Event Edge Cases
    def test_update_event_pending(self):
        url = reverse('stsv_app:event-detail', kwargs={'pk': self.pending_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        response = self.client.patch(url, {"title": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Không thể chỉnh sửa sự kiện đang chờ duyệt hoặc đã duyệt.", str(response.data))

    def test_update_event_draft(self):
        url = reverse('stsv_app:event-detail', kwargs={'pk': self.draft_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        response = self.client.patch(url, {"title": "Updated", "status": "PENDING"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft_event.refresh_from_db()
        self.assertEqual(self.draft_event.status, Event.Status.PENDING)

    # 2. Approve/Reject Edge Cases
    def test_student_approve_event(self):
        url = reverse('stsv_app:event-approve', kwargs={'pk': self.pending_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        # Test for other roles getting 403 inside the method
        org2 = User.objects.create(username="org2", role=User.Role.ORGOFFICER)
        url = reverse('stsv_app:event-send-reminder', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=org2)
        response = self.client.post(url, {"title": "Test", "message": "Test"})
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_anonymous_user(self):
        service = EventService(AnonymousUser())
        self.assertFalse(service.get_events_for_user(Event.objects.all()).exists())
        self.assertFalse(service.get_event_suggestions().exists())

    def test_create_event_invalid_status_and_pending(self):
        url = reverse('stsv_app:event-list')
        self.client.force_authenticate(user=self.org_officer)
        res1 = self.client.post(url, {
            "title": "Invalid Status",
            "description": "Test",
            "status": "APPROVED",
            "start_time": (timezone.now() + datetime.timedelta(days=1)).isoformat(),
            "end_time": (timezone.now() + datetime.timedelta(days=2)).isoformat(),
            "category": self.category.id,
            "max_participants": 10,
            "location": "A1"
        }, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res1.data['status'], 'DRAFT')

        # PENDING should trigger notify admins
        # Remove all admins first to test line 144 (if not admins.exists(): return)
        User.objects.filter(role=User.Role.ADMIN).delete()
        res2 = self.client.post(url, {
            "title": "Pending Event",
            "description": "Test",
            "status": "PENDING",
            "start_time": (timezone.now() + datetime.timedelta(days=1)).isoformat(),
            "end_time": (timezone.now() + datetime.timedelta(days=2)).isoformat(),
            "category": self.category.id,
            "max_participants": 10,
            "location": "A1"
        }, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.data['status'], 'PENDING')

    def test_update_event_invalid_status(self):
        url = reverse('stsv_app:event-detail', kwargs={'pk': self.draft_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        # Attempt to change to APPROVED (invalid for org officer)
        res = self.client.patch(url, {"status": "APPROVED"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.draft_event.refresh_from_db()
        self.assertEqual(self.draft_event.status, 'DRAFT')

    def test_approve_reject_by_org_officer(self):
        # org_officer can see pending_event, but cannot approve/reject it
        url_approve = reverse('stsv_app:event-approve', kwargs={'pk': self.pending_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        res = self.client.post(url_approve)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Bạn không có quyền duyệt sự kiện này", str(res.data))

        url_reject = reverse('stsv_app:event-reject', kwargs={'pk': self.pending_event.pk})
        res2 = self.client.post(url_reject, {"reason": "Test"})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Bạn không có quyền từ chối sự kiện này", str(res2.data))

    def test_reject_event_not_pending(self):
        url_reject = reverse('stsv_app:event-reject', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(url_reject, {"reason": "Test"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Chỉ có thể từ chối sự kiện đang chờ duyệt.", str(res.data))

    def test_reregister_after_cancelled(self):
        # First register
        url_reg = reverse('stsv_app:event-register', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        self.client.post(url_reg)

        # Then cancel
        url_cancel = reverse('stsv_app:event-cancel-registration', kwargs={'pk': self.approved_event.pk})
        self.client.delete(url_cancel)

        # Re-register
        res = self.client.post(url_reg)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        reg = EventRegistration.objects.get(event=self.approved_event, student=self.student.student_profile)
        self.assertEqual(reg.status, EventRegistration.Status.REGISTERED)

    def test_checkin_twice(self):
        self.approved_event.is_youth_union = True
        self.approved_event.save()

        # Register
        url_reg = reverse('stsv_app:event-register', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        self.client.post(url_reg)

        session = CheckInSession.objects.create(event=self.approved_event, expires_at=timezone.now() + datetime.timedelta(minutes=10), dynamic_code="TWICE_CODE")
        url_checkin = reverse('stsv_app:event-check-in', kwargs={'pk': self.approved_event.pk})

        # Checkin first time
        res1 = self.client.post(url_checkin, {"dynamic_code": "TWICE_CODE"}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Checkin second time
        res2 = self.client.post(url_checkin, {"dynamic_code": "TWICE_CODE"}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Bạn đã điểm danh rồi.", str(res2.data))

    def test_send_reminder_groups(self):
        # Register a student
        url_reg = reverse('stsv_app:event-register', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        self.client.post(url_reg)

        url = reverse('stsv_app:event-send-reminder', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.admin)

        # WAITLIST
        res_w = self.client.post(url, {"title": "T", "message": "M", "target_group": "WAITLIST"})
        self.assertEqual(res_w.status_code, status.HTTP_200_OK)

        # CHECKED_IN
        res_c = self.client.post(url, {"title": "T", "message": "M", "target_group": "CHECKED_IN"})
        self.assertEqual(res_c.status_code, status.HTTP_200_OK)

        # ALL
        res_a = self.client.post(url, {"title": "T", "message": "M", "target_group": "ALL"})
        self.assertEqual(res_a.status_code, status.HTTP_200_OK)

        # INVALID
        res_i = self.client.post(url, {"title": "T", "message": "M", "target_group": "INVALID"})
        self.assertEqual(res_i.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Nhóm đối tượng không hợp lệ", str(res_i.data))

    def test_view_get_serializer_class(self):
        view = EventViewSet()

        view.action = 'check_in'
        self.assertEqual(view.get_serializer_class(), CheckInRequestSerializer)

        view.action = 'sessions'
        self.assertEqual(view.get_serializer_class(), CheckInSessionSerializer)

        view.action = 'register'
        self.assertEqual(view.get_serializer_class(), serializers.Serializer)

        view.action = 'cancel_registration'
        self.assertEqual(view.get_serializer_class(), serializers.Serializer)

    def test_view_sessions_endpoints(self):
        url = reverse('stsv_app:event-sessions', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.org_officer)

        # GET sessions
        res_get = self.client.get(url)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)

        # POST valid session (no data needed since fields are read_only)
        res_post_valid = self.client.post(url, {}, format='json')
        self.assertEqual(res_post_valid.status_code, status.HTTP_201_CREATED)

    def test_admin_approve_approved_event(self):
        url = reverse('stsv_app:event-approve', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_reject_event_no_reason(self):
        url = reverse('stsv_app:event-reject', kwargs={'pk': self.pending_event.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Vui lòng cung cấp lý do từ chối.", str(response.data))

    # 3. Registration & Waitlist
    def test_register_event_full(self):
        student2_user = User.objects.create(username="s2", role=User.Role.STUDENT)
        student2_profile = StudentProfile.objects.create(user=student2_user, student_id="S02", full_name="S2")

        student3_user = User.objects.create(username="s3", role=User.Role.STUDENT)
        student3_profile = StudentProfile.objects.create(user=student3_user, student_id="S03", full_name="S3")

        url = reverse('stsv_app:event-register', kwargs={'pk': self.approved_event.pk})

        # S1 đăng ký thành công (kín chỗ vì max = 1)
        self.client.force_authenticate(user=self.student)
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # S2 đăng ký vào danh sách chờ (kín chỗ chờ vì waitlist_cap = 1)
        self.client.force_authenticate(user=student2_user)
        res2 = self.client.post(url)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventRegistration.objects.get(student=student2_profile).status, EventRegistration.Status.WAITLIST)

        # S3 đăng ký thất bại vì danh sách chờ đã đầy
        self.client.force_authenticate(user=student3_user)
        res3 = self.client.post(url)
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

        # S1 hủy đăng ký -> S2 được lên danh sách chính thức
        self.client.force_authenticate(user=self.student)
        res_cancel = self.client.delete(reverse('stsv_app:event-cancel-registration', kwargs={'pk': self.approved_event.pk}))
        self.assertEqual(res_cancel.status_code, status.HTTP_204_NO_CONTENT)

        reg2 = EventRegistration.objects.get(student=student2_profile)
        self.assertEqual(reg2.status, EventRegistration.Status.REGISTERED)

    def test_cancel_registration_not_registered(self):
        url = reverse('stsv_app:event-cancel-registration', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_already_registered(self):
        url = reverse('stsv_app:event-register', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 4. Checkin Edge Cases
    def test_checkin_no_code(self):
        url = reverse('stsv_app:event-check-in', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cần cung cấp dynamic_code", str(response.data))

    def test_checkin_invalid_code(self):
        url = reverse('stsv_app:event-check-in', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, {"dynamic_code": "INVALID"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Mã điểm danh không hợp lệ.", str(response.data))

    def test_checkin_expired_code(self):
        session = CheckInSession.objects.create(event=self.approved_event, expires_at=timezone.now() - datetime.timedelta(minutes=10), dynamic_code="TEST_CODE_1")
        url = reverse('stsv_app:event-check-in', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, {"dynamic_code": str(session.dynamic_code)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Phiên điểm danh đã hết hạn.", str(response.data))

    def test_checkin_not_registered(self):
        session = CheckInSession.objects.create(event=self.approved_event, expires_at=timezone.now() + datetime.timedelta(minutes=10), dynamic_code="TEST_CODE_2")
        url = reverse('stsv_app:event-check-in', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, {"dynamic_code": str(session.dynamic_code)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Không tìm thấy thông tin đăng ký", str(response.data))

    # 5. Event Statistics
    def test_statistics_student_access(self):
        url = reverse('stsv_app:event-statistics', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_statistics_other_org_officer(self):
        org2 = User.objects.create(username="org2", role=User.Role.ORGOFFICER)
        OrgProfile.objects.create(user=org2, org_name="O2", org_type=OrgProfile.OrgType.CLUB)

        url = reverse('stsv_app:event-statistics', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=org2)
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    # 6. Send Reminder
    def test_send_reminder_student(self):
        url = reverse('stsv_app:event-send-reminder', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, {"title": "T", "message": "M", "target_group": "ALL"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_reminder_no_content(self):
        url = reverse('stsv_app:event-send-reminder', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        response = self.client.post(url, {"target_group": "ALL"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_reminder_invalid_target(self):
        url = reverse('stsv_app:event-send-reminder', kwargs={'pk': self.approved_event.pk})
        self.client.force_authenticate(user=self.org_officer)
        response = self.client.post(url, {"title": "T", "message": "M", "target_group": "INVALID"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
