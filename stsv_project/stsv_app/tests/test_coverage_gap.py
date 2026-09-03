# Standard library
import datetime

# Django
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

# Django REST Framework
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APITestCase

# Third-party
from unittest import mock

# App imports
from stsv_app.models import EventCategory, Event, User, OrgProfile, LecturerProfile, Faculty
from stsv_app.models.academics import Schedule, CourseClass, Subject, Semester, StudentCourse
from stsv_app.models.events import EventRegistration, YouthUnionRecord
from stsv_app.models.support import FacilityReport
from stsv_app.models.training_points import TrainingCriterion
from stsv_app.renderers import UnifiedJSONRenderer
from stsv_app.serializers.events import EventSerializer
from stsv_app.serializers.users import CustomTokenRefreshSerializer
from stsv_app.services.academics import SubjectService
from stsv_app.services.events import EventService
from stsv_app.services.exceptions import ValidationError
from stsv_app.services.payments.base import BasePaymentProvider
from stsv_app.services.payments.providers.momo import MoMoProvider
from stsv_app.services.payments.providers.vnpay import VNPayProvider
from stsv_app.services.push_notification import PushNotificationService
from stsv_app.tests.base import BaseAPITestCase
from stsv_app.views.finance import PaymentViewSet, MockRedirectView
from stsv_app.views.support import ComplaintViewSet
from stsv_app.views.system import UserNotificationViewSet


class CoverageGapTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create(username="admin_gap", role=User.Role.ADMIN)
        self.org_user = User.objects.create(username="org_gap", role=User.Role.ORGOFFICER)

        self.faculty = Faculty.objects.create(code="F_GAP", name="Faculty Gap")
        self.org_profile = OrgProfile.objects.create(user=self.org_user, org_name="Org Gap", org_type=OrgProfile.OrgType.CLUB)

        self.criterion = TrainingCriterion.objects.create(code="T1", name="T1", max_points=10)

        self.category = EventCategory.objects.create(name="Cat Gap", criterion=self.criterion)
        self.event = Event.objects.create(
            title="Event Gap", category=self.category, organizer=self.org_user,
            start_time=timezone.now(), end_time=timezone.now() + datetime.timedelta(days=1),
            max_participants=10
        )

    def test_models_str(self):
        self.assertEqual(str(self.category), "Cat Gap")
        self.assertEqual(str(self.event), "Event Gap")

    def test_renderers(self):
        renderer = UnifiedJSONRenderer()
        data = {"status": "ok", "data": {}}
        rendered = renderer.render(data, renderer_context={})
        self.assertTrue(rendered is not None)

    def test_serializers_events_unauth(self):
        serializer = EventSerializer(self.event, context={'request': None})
        self.assertEqual(serializer.data['user_registration_status'], 'UNREGISTERED')

    def test_serializers_users_refresh_invalid(self):
        serializer = CustomTokenRefreshSerializer(data={'refresh': 'invalid_token'})
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)

    def test_services_academics(self):
        service = SubjectService()
        qs = service.get_subjects_for_user(self.admin)
        self.assertTrue(qs is not None)

    def test_services_events_permissions(self):
        org_user2 = User.objects.create(username="org_gap2", role=User.Role.ORGOFFICER)
        service = EventService(org_user2)
        with self.assertRaises(ValidationError):
            service.get_event_statistics(self.event)
        with self.assertRaises(ValidationError):
            service.send_event_reminder(self.event, "Title", "Message")

    def test_services_payments_base(self):
        class DummyProvider(BasePaymentProvider):
            def generate_payment_url(self, t, a, o, r):
                return super().generate_payment_url(t, a, o, r)
            def verify_webhook(self, data):
                return super().verify_webhook(data)

        dummy = DummyProvider()
        self.assertIsNone(dummy.generate_payment_url("1", 1.0, "i", "r"))
        self.assertIsNone(dummy.verify_webhook({}))

    @mock.patch('django.conf.settings.MOMO_CONFIG', {})
    def test_services_payments_momo(self):
        provider = MoMoProvider()
        self.assertTrue(provider.verify_webhook({'resultCode': 0}))

    @mock.patch('django.conf.settings.VNPAY_CONFIG', {})
    def test_services_payments_vnpay(self):
        provider = VNPayProvider()
        self.assertTrue(provider.verify_webhook({'vnp_ResponseCode': '00'}))

    @mock.patch.dict('sys.modules', {'firebase_admin': None})
    def test_services_push_notification_import_error(self):
        service = PushNotificationService()
        self.assertFalse(service.send_push_notification(self.admin, "T", "B"))

    @mock.patch('stsv_app.views.events.CheckInSessionSerializer')
    def test_views_events_sessions_invalid(self, mock_serializer_class):
        mock_instance = mock.Mock()
        mock_instance.is_valid.return_value = False
        mock_instance.errors = {'detail': 'mock error'}
        mock_serializer_class.return_value = mock_instance
        url = reverse('stsv_app:event-sessions', kwargs={'pk': self.event.pk})
        self.client.force_authenticate(user=self.org_user)
        res = self.client.post(url, {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_views_users_me_org_and_admin(self):
        url = reverse('stsv_app:user-me')
        self.client.force_authenticate(user=self.org_user)
        res1 = self.client.get(url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.admin)
        res2 = self.client.get(url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    def test_views_users_devices_invalid(self):
        url = reverse('stsv_app:user-register-device')
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(url, {'device_os': 'WINDOWS'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_views_finance_payment_queryset(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.admin
        view = PaymentViewSet()
        view.request = Request(request)
        view.format_kwarg = None
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 0)

    @mock.patch('cloudinary.uploader.upload_resource')
    def test_views_support_facility(self, mock_upload):
        mock_upload.return_value = {}
        report = FacilityReport.objects.create(
            reporter=self.admin,
            room="A1", description="Broken", status=FacilityReport.Status.PENDING
        )
        url = reverse('stsv_app:facility-report-resolve-report', kwargs={'pk': report.pk})

        # Test non-admin to hit line 59
        self.client.force_authenticate(user=self.org_user)
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, status.HTTP_403_FORBIDDEN)

        # Test admin to hit line 66
        self.client.force_authenticate(user=self.admin)
        dummy_file = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpeg")
        res2 = self.client.post(url, {'resolution_image': dummy_file}, format='multipart')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    def test_services_events_attended_regs(self):
        EventRegistration.objects.create(
            event=self.event,
            student=self.student.student_profile,
            status=EventRegistration.Status.REGISTERED,
            is_checked_in=True
        )
        # Call the serializer that uses EventSerializer to cover serializers/events.py line 66
        req = mock.Mock()
        req.user = self.student
        serializer = EventSerializer(self.event, context={'request': req})
        self.assertEqual(serializer.data['user_registration_status'], 'REGISTERED')

        # Call EventService to cover services/events.py loop (line 218)
        service = EventService(self.student)
        res = service.sync_youth_union_records()

        # Test line 67 (reg.status == CANCELLED)
        EventRegistration.objects.all().delete()
        EventRegistration.objects.create(
            event=self.event,
            student=self.student.student_profile,
            status=EventRegistration.Status.CANCELLED,
            is_checked_in=False
        )
        serializer2 = EventSerializer(self.event, context={'request': req})
        self.assertEqual(serializer2.data['user_registration_status'], 'UNREGISTERED')


# ============================================================
# Tests bổ sung để phủ 11 dòng còn thiếu
# ============================================================

class MissingCoverageTestCase(BaseAPITestCase):
    """Phủ các nhánh còn thiếu sau lần chạy coverage trước."""

    # ----------------------------------------------------------
    # momo.py L21 & vnpay.py L17: nhánh mock_redirect_base
    # ----------------------------------------------------------
    @override_settings(MOMO_CONFIG={})
    def test_momo_no_config_with_mock_redirect_base(self):
        """Khi truyền mock_redirect_base, MoMo bọc return_url vào mock base URL."""
        provider = MoMoProvider()
        url = provider.generate_payment_url(
            transaction_id="ORDER123",
            amount=100000,
            order_info="Test",
            return_url="https://test.com/return",
            mock_redirect_base="https://mock.base/redirect",
        )
        self.assertTrue(url.startswith("https://mock.base/redirect"))
        self.assertIn("return_url=", url)

    @override_settings(VNPAY_CONFIG={})
    def test_vnpay_no_config_with_mock_redirect_base(self):
        """Khi truyền mock_redirect_base, VNPay bọc return_url vào mock base URL."""
        provider = VNPayProvider()
        url = provider.generate_payment_url(
            transaction_id="ORDER123",
            amount=100000,
            order_info="Test",
            return_url="https://test.com/vnpay/return",
            mock_redirect_base="https://mock.base/redirect",
        )
        self.assertTrue(url.startswith("https://mock.base/redirect"))
        self.assertIn("return_url=", url)

    # ----------------------------------------------------------
    # views/finance.py L17-33: MockRedirectView.get()
    # ----------------------------------------------------------
    def test_mock_redirect_view(self):
        """MockRedirectView trả về HTML chứa return_url."""
        url = reverse('stsv_app:mock-redirect')
        response = self.client.get(url, {'return_url': 'stsvapp://payment/result?resultCode=0'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'stsvapp://payment/result', response.content)

    # ----------------------------------------------------------
    # views/support.py L17: get_queryset khi chưa auth
    # ----------------------------------------------------------
    def test_complaint_queryset_unauthenticated(self):
        """get_queryset của ComplaintViewSet trả về none() khi chưa xác thực."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        view = ComplaintViewSet()
        view.request = Request(request)
        view.format_kwarg = None
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 0)

    # ----------------------------------------------------------
    # views/system.py L43: get_queryset khi chưa auth
    # ----------------------------------------------------------
    def test_notification_queryset_unauthenticated(self):
        """get_queryset của UserNotificationViewSet trả về none() khi chưa xác thực."""
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        view = UserNotificationViewSet()
        view.request = Request(request)
        view.format_kwarg = None
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 0)

    # ----------------------------------------------------------
    # services/events.py L177: register_event trên sự kiện DRAFT
    # ----------------------------------------------------------
    def test_register_event_not_approved_raises(self):
        """L177: raise ValidationError khi sự kiện chưa được duyệt."""
        criterion = TrainingCriterion.objects.first()
        cat = EventCategory.objects.create(name="Cat Miss177", criterion=criterion)
        draft_event = Event.objects.create(
            title="Draft Miss177",
            category=cat,
            organizer=self.org_officer,
            start_time=timezone.now() + datetime.timedelta(days=10),
            end_time=timezone.now() + datetime.timedelta(days=11),
            max_participants=50,
            status=Event.Status.DRAFT,
        )
        service = EventService(self.student)
        with self.assertRaises(ValidationError):
            service.register_event(draft_event)

    # ----------------------------------------------------------
    # services/events.py L206: trùng lịch sự kiện khác
    # ----------------------------------------------------------
    def test_register_event_overlapping_event_raises(self):
        """L206: raise ValidationError khi trùng giờ với sự kiện đã đăng ký."""
        criterion = TrainingCriterion.objects.first()
        cat = EventCategory.objects.create(name="Cat Overlap206", criterion=criterion)
        base_time = timezone.now() + datetime.timedelta(days=30)

        event1 = Event.objects.create(
            title="Overlap Event 1",
            category=cat,
            organizer=self.org_officer,
            start_time=base_time,
            end_time=base_time + datetime.timedelta(hours=3),
            max_participants=50,
            status=Event.Status.APPROVED,
        )
        EventRegistration.objects.create(
            event=event1,
            student=self.student.student_profile,
            status=EventRegistration.Status.REGISTERED,
        )

        event2 = Event.objects.create(
            title="Overlap Event 2",
            category=cat,
            organizer=self.org_officer,
            start_time=base_time + datetime.timedelta(hours=1),
            end_time=base_time + datetime.timedelta(hours=4),
            max_participants=50,
            status=Event.Status.APPROVED,
        )
        service = EventService(self.student)
        with self.assertRaises(ValidationError):
            service.register_event(event2)

    # ----------------------------------------------------------
    # services/events.py L223: trùng lịch học (exact_date schedule)
    # ----------------------------------------------------------
    def test_register_event_overlapping_schedule_raises(self):
        """L223: raise ValidationError khi trùng lịch học (exact_date)."""
        semester = Semester.objects.first()
        subject = Subject.objects.first()
        if not semester or not subject:
            self.skipTest("Không có semester/subject trong DB test")  # pragma: no cover

        criterion = TrainingCriterion.objects.first()
        cat = EventCategory.objects.create(name="Cat Sched223", criterion=criterion)

        today = timezone.now().date()
        days_ahead = (7 - today.weekday()) % 7 or 7
        event_date = today + datetime.timedelta(days=days_ahead)
        event_start = datetime.datetime.combine(event_date, datetime.time(8, 0))
        event_end = event_start + datetime.timedelta(hours=2)

        course_class = CourseClass.objects.create(
            class_code=f"CC-SCHED223-{event_date}",
            subject=subject,
            semester=semester,
            lecturer=self.lecturer.lecturer_profile,
        )
        StudentCourse.objects.get_or_create(
            student=self.student.student_profile,
            course_class=course_class,
        )
        Schedule.objects.create(
            course_class=course_class,
            day_of_week=2,
            start_time=datetime.time(7, 30),
            end_time=datetime.time(9, 30),
            exact_date=event_date,
            room="P.101",
        )

        event = Event.objects.create(
            title="Event Sched223",
            category=cat,
            organizer=self.org_officer,
            start_time=event_start,
            end_time=event_end,
            max_participants=50,
            status=Event.Status.APPROVED,
        )
        service = EventService(self.student)
        with self.assertRaises(ValidationError):
            service.register_event(event)

    # ----------------------------------------------------------
    # services/events.py L252: sync_youth_union_records loop
    # ----------------------------------------------------------
    def test_sync_youth_union_with_youth_union_event(self):
        """L252: sync_youth_union_records tạo YouthUnionRecord khi is_youth_union=True và is_checked_in=True."""
        criterion = TrainingCriterion.objects.first()
        cat = EventCategory.objects.create(name="Cat YU252", criterion=criterion)
        event = Event.objects.create(
            title="Youth Union Event 252",
            category=cat,
            organizer=self.org_officer,
            start_time=timezone.now() - datetime.timedelta(days=2),
            end_time=timezone.now() - datetime.timedelta(days=1),
            max_participants=50,
            status=Event.Status.APPROVED,
            is_youth_union=True,
        )
        EventRegistration.objects.create(
            event=event,
            student=self.student.student_profile,
            status=EventRegistration.Status.REGISTERED,
            is_checked_in=True,
        )

        service = EventService(self.student)
        service.sync_youth_union_records()

        self.assertTrue(
            YouthUnionRecord.objects.filter(
                student=self.student.student_profile,
                event=event,
            ).exists()
        )
