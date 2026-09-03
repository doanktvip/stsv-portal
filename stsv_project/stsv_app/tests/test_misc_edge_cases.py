# Standard library
import datetime

# Django
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

# Django REST Framework
from rest_framework import status
from rest_framework.test import APITestCase

# Third-party
from unittest import mock

# App imports
from stsv_app.models.academics import Subject, Semester, CourseClass, ScoreComponent, StudentCourse
from stsv_app.models.core import Faculty, Major, Cohort, HomeroomClass
from stsv_app.models.events import EventCategory, Event, EventRegistration
from stsv_app.models.finance import Fee, Payment
from stsv_app.models.support import Complaint
from stsv_app.models.system import SystemConfig
from stsv_app.models.training_points import TrainingCriterion
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile
from stsv_app.tests.base import BaseAPITestCase


class MiscEdgeCasesTestCase(BaseAPITestCase):
    def setUp(self):
        # Create user without profile
        self.student_no_profile = User.objects.create(username="s_no_profile", role=User.Role.STUDENT)
        self.org_user = User.objects.create(username="org_user", role=User.Role.ORGOFFICER)

        # Create student with profile
        self.student_user = User.objects.create(username="student1", role=User.Role.STUDENT)
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user, student_id="ST1",
            faculty=Faculty.objects.create(code="F1", name="Faculty 1"),
            major=Major.objects.create(code="M1", name="Major 1", faculty=Faculty.objects.first()),
            cohort=Cohort.objects.create(code="C1", enrollment_year=2023)
        )

        # Basic objects for relationships
        self.semester = Semester.objects.create(code="HK1", start_date=datetime.date(2023, 9, 1), end_date=datetime.date(2024, 1, 1))
        self.subject = Subject.objects.create(subject_code="SUB1", name="Subject 1", credits=3, faculty=self.student_profile.faculty)
        self.course_class = CourseClass.objects.create(subject=self.subject, semester=self.semester, class_code="CLASS1")
        self.score_component = ScoreComponent.objects.create(subject=self.subject, name="Midterm", weight_percentage=30)
        self.student_course = StudentCourse.objects.create(student=self.student_profile, course_class=self.course_class)

        # Event data
        self.criterion = TrainingCriterion.objects.create(name="Crit1", max_points=10)
        self.category = EventCategory.objects.create(name="Cat1", criterion=self.criterion)
        self.event_ongoing = Event.objects.create(
            title="Ongoing Event", category=self.category, organizer=self.org_user,
            start_time=timezone.now() - datetime.timedelta(days=1),
            end_time=timezone.now() + datetime.timedelta(days=1),
            status=Event.Status.APPROVED, max_participants=100
        )
        self.event_closed = Event.objects.create(
            title="Closed Event", category=self.category, organizer=self.org_user,
            start_time=timezone.now() - datetime.timedelta(days=2),
            end_time=timezone.now() - datetime.timedelta(days=1),
            status=Event.Status.APPROVED, max_participants=100
        )

        # Finance data
        self.fee = Fee.objects.create(
            title="Fee 1", amount=100000,
            fee_type=Fee.FeeType.TUITION,
            content_type=ContentType.objects.get_for_model(Semester),
            object_id=self.semester.id,
            creator=self.admin,
            due_date=timezone.now() + datetime.timedelta(days=30)
        )

    def test_models_str(self):
        # Covers models/academics.py __str__ methods
        self.assertEqual(str(self.subject), "Subject 1")
        self.assertEqual(str(self.semester), "HK1")
        self.assertEqual(str(self.course_class), "Subject 1 - CLASS1")
        self.assertEqual(str(self.score_component), "Subject 1 - Midterm (30%)")
        self.assertEqual(str(self.student_course), "ST1 - CLASS1")

        # core.py
        self.assertEqual(str(self.student_profile.faculty), "F1 - Faculty 1")
        self.assertEqual(str(self.student_profile.major), "M1 - Major 1")
        self.assertEqual(str(self.student_profile.cohort), "C1")
        homeroom = HomeroomClass.objects.create(name="HR1", major=self.student_profile.major, cohort=self.student_profile.cohort)
        self.assertEqual(str(homeroom), "HR1")

        # finance.py
        self.assertEqual(str(self.fee), "Fee 1 - 100000")
        payment = Payment.objects.create(student=self.student_profile, fee=self.fee, amount=100000, transaction_id="TXN123", payment_method=Payment.Method.MOMO)
        self.assertEqual(str(payment), f"Payment {payment.id} - ST1 - PENDING")

        # users.py
        l_prof = LecturerProfile.objects.create(user=self.org_user, lecturer_id="L1", full_name="Lec 1")
        self.assertEqual(str(l_prof), "Lec 1")
        self.student_profile.full_name = "Student 1"
        self.student_profile.save()
        self.assertEqual(str(self.student_profile), "ST1 - Student 1")
        o_prof = OrgProfile.objects.create(user=self.org_user, org_name="Org 1")
        self.assertEqual(str(o_prof), "Org 1")

        # system.py
        sys_conf = SystemConfig.objects.create(key="k1", value="v1", updated_by=self.admin)
        self.assertEqual(str(sys_conf), "k1")

    def test_users_views_profile_not_found(self):
        url = reverse('stsv_app:user-me')
        self.client.force_authenticate(user=self.student_no_profile)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_support_create_complaint(self):
        url = reverse('stsv_app:complaint-list')
        self.client.force_authenticate(user=self.student_user)
        res = self.client.post(url, {
            "title": "Help",
            "description": "Please help"
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_events_serializers_states(self):
        # Covers ONGOING, CLOSED, WAITING_LIST in events.py serializers
        url_ongoing = reverse('stsv_app:event-detail', kwargs={'pk': self.event_ongoing.pk})
        url_closed = reverse('stsv_app:event-detail', kwargs={'pk': self.event_closed.pk})

        self.client.force_authenticate(user=self.admin)
        res1 = self.client.get(url_ongoing)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data['event_state'], 'ONGOING')
        self.assertEqual(res1.data['user_registration_status'], 'UNREGISTERED')  # No profile

        res2 = self.client.get(url_closed)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data['event_state'], 'CLOSED')

        # Test WAITING_LIST
        EventRegistration.objects.create(
            event=self.event_ongoing,
            student=self.student_profile,
            status=EventRegistration.Status.WAITLIST,
            queue_position=1
        )
        self.client.force_authenticate(user=self.student_user)
        res3 = self.client.get(url_ongoing)
        self.assertEqual(res3.data['user_registration_status'], 'WAITING_LIST')

    def test_finance_queryset_non_student(self):
        url = reverse('stsv_app:payment-list')
        self.client.force_authenticate(user=self.org_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('stsv_app.services.payments.providers.momo.MoMoProvider.generate_payment_url')
    def test_finance_create_payment(self, mock_generate):
        mock_generate.return_value = "http://momo.vn/pay"
        url = reverse('stsv_app:payment-list')
        self.client.force_authenticate(user=self.student_user)

        # Without return_url (defaults to stsvapp://payment-return)
        res1 = self.client.post(url, {
            "fee": self.fee.id,
            "payment_method": "MOMO",
            "amount": "100000"
        }, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment_url", res1.data)

        # Mock exception
        mock_generate.side_effect = Exception("Gateway error")
        res2 = self.client.post(url, {
            "fee": self.fee.id,
            "payment_method": "MOMO",
            "amount": "100000"
        }, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finance_refund_already_requested(self):
        # Create successful payment
        payment = Payment.objects.create(
            student=self.student_profile, fee=self.fee, amount=100000,
            payment_method=Payment.Method.MOMO, status=Payment.Status.SUCCESS,
            refund_status=Payment.RefundStatus.REQUESTED
        )
        url = reverse('stsv_app:payment-refund', kwargs={'pk': payment.pk})
        self.client.force_authenticate(user=self.student_user)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Refund already requested", str(res.data))
