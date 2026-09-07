from django.test import RequestFactory
from django.utils import timezone
from datetime import timedelta
from .base import BaseAPITestCase
from stsv_app.models import (
    Event, EventCategory, EventRegistration, 
    FeeCampaign, Payment,
    PointTransaction
)
from stsv_app.serializers import (
    EventSerializer, FeeCampaignSerializer, 
    PointTransactionSerializer
)
from unittest.mock import Mock

class SerializersEdgeCasesTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def test_event_state_ongoing_and_closed(self):
        cat = EventCategory.objects.create(name="Cat")
        # Ongoing
        now = timezone.now()
        event1 = Event.objects.create(
            title="E1", category=cat, organizer=self.org_officer.org_profile,
            start_time=now - timedelta(days=1), end_time=now + timedelta(days=1)
        )
        serializer1 = EventSerializer(event1)
        self.assertEqual(serializer1.data['event_state'], 'ONGOING')

        # Closed
        event2 = Event.objects.create(
            title="E2", category=cat, organizer=self.org_officer.org_profile,
            start_time=now - timedelta(days=2), end_time=now - timedelta(days=1)
        )
        serializer2 = EventSerializer(event2)
        self.assertEqual(serializer2.data['event_state'], 'CLOSED')

    def test_event_user_registration_status_unauthenticated(self):
        cat = EventCategory.objects.create(name="Cat")
        event = Event.objects.create(
            title="E", category=cat, organizer=self.org_officer.org_profile,
            start_time=timezone.now(), end_time=timezone.now()
        )
        request = self.factory.get('/')
        request.user = Mock(is_authenticated=False)
        serializer = EventSerializer(event, context={'request': request})
        self.assertEqual(serializer.data['user_registration_status'], 'UNREGISTERED')

    def test_event_user_registration_status_waitlist(self):
        cat = EventCategory.objects.create(name="Cat")
        event = Event.objects.create(
            title="E", category=cat, organizer=self.org_officer.org_profile,
            start_time=timezone.now(), end_time=timezone.now()
        )
        request = self.factory.get('/')
        request.user = self.student
        EventRegistration.objects.create(event=event, student=self.student.student_profile, status=EventRegistration.Status.WAITLIST)
        serializer = EventSerializer(event, context={'request': request})
        self.assertEqual(serializer.data['user_registration_status'], 'WAITING_LIST')
        
    def test_event_user_registration_status_not_student(self):
        cat = EventCategory.objects.create(name="Cat")
        event = Event.objects.create(
            title="E", category=cat, organizer=self.org_officer.org_profile,
            start_time=timezone.now(), end_time=timezone.now()
        )
        request = self.factory.get('/')
        request.user = self.org_officer # No student profile
        serializer = EventSerializer(event, context={'request': request})
        self.assertEqual(serializer.data['user_registration_status'], 'UNREGISTERED')

    def test_feecampaign_get_vietqr_url_no_method(self):
        # Mock object without get_vietqr_url
        obj = Mock()
        del obj.get_vietqr_url
        serializer = FeeCampaignSerializer(obj)
        self.assertEqual(serializer.get_vietqr_url(obj), "")

    def test_feecampaign_get_paid_count(self):
        obj = Mock()
        del obj.paid_count_annotated
        del obj.payments
        serializer = FeeCampaignSerializer(obj)
        self.assertEqual(serializer.get_paid_count(obj), 0)

    def test_feecampaign_get_total_students(self):
        obj = Mock()
        del obj.total_students_annotated
        del obj.homeroom_class
        serializer = FeeCampaignSerializer(obj)
        self.assertEqual(serializer.get_total_students(obj), 0)

    def test_feecampaign_get_my_payment_status(self):
        campaign = FeeCampaign.objects.create(title="C1", amount=10, creator=self.bancansu)
        request = self.factory.get('/')
        request.user = self.student
        serializer = FeeCampaignSerializer(campaign, context={'request': request})
        self.assertIsNone(serializer.data['my_payment_status'])
        
        # Also test with payments prefetched manually
        setattr(campaign, '_prefetched_user_payments', [])
        serializer = FeeCampaignSerializer(campaign, context={'request': request})
        self.assertIsNone(serializer.data['my_payment_status'])
        
        payment = Payment.objects.create(campaign=campaign, student=self.student.student_profile, amount=10, status=Payment.Status.SUCCESS)
        setattr(campaign, '_prefetched_user_payments', [payment])
        serializer = FeeCampaignSerializer(campaign, context={'request': request})
        self.assertIsNotNone(serializer.data['my_payment_status'])

    def test_pointtransaction_get_criterion_code(self):
        # No event, no rule
        tx = PointTransaction.objects.create(student=self.student.student_profile, semester_id=1, points_changed=10, reason="test")
        serializer = PointTransactionSerializer(tx)
        self.assertEqual(serializer.data['criterion_code'], "Khác")
        
        # Event with category but no criterion
        cat = EventCategory.objects.create(name="Cat No Criterion")
        event = Event.objects.create(
            title="E", category=cat, organizer=self.org_officer.org_profile,
            start_time=timezone.now(), end_time=timezone.now()
        )
        tx.event = event
        tx.save()
        serializer = PointTransactionSerializer(tx)
        self.assertEqual(serializer.data['criterion_code'], "Khác")
