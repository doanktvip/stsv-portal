from django.utils import timezone
from datetime import timedelta
import random
import uuid
from stsv_app.models.events import EventCategory, Event, CheckInSession, EventRegistration
from stsv_app.models.users import OrgProfile, StudentProfile
from stsv_app.models.training_points import TrainingCriterion


def seed_events(num_events=20):
    print("--- Seeding Events Data ---")
    now = timezone.now()
    
    criterion = TrainingCriterion.objects.first()
    if not criterion:
        criterion, _ = TrainingCriterion.objects.get_or_create(code="HTKH", defaults={"name": "Hội thảo KH", "max_points": 10})

    cat, _ = EventCategory.objects.get_or_create(name="Hội thảo khoa học", defaults={"criterion": criterion})
    
    orgs = list(OrgProfile.objects.all())
    students = list(StudentProfile.objects.all())
    if not orgs or not students:
        print("Missing Orgs or Students. Skipping events.")
        return

    events_to_create = []
    
    # Generate bulk events
    print(f"Seeding {num_events} Events...")
    for i in range(num_events):
        org = random.choice(orgs)
        # Deterministic status to cover all cases
        status = Event.Status.choices[i % len(Event.Status.choices)][0]
        
        # Random time (past, present, future)
        start_offset = random.randint(-30, 30)
        start_time = now + timedelta(days=start_offset, hours=random.randint(8, 16))
        end_time = start_time + timedelta(hours=random.randint(2, 4))
        
        events_to_create.append(Event(
            title=f"Sự kiện {random.randint(100, 999)}",
            description="Đây là sự kiện mẫu được tạo tự động.",
            category=cat,
            organizer=org.user,
            start_time=start_time,
            end_time=end_time,
            location=f"Hội trường {random.choice(['A', 'B', 'C'])}",
            max_participants=random.randint(50, 500),
            status=status,
            cover_image="https://dummyimage.com/600x400/000/fff.jpg&text=Event"
        ))
        
    if events_to_create:
        Event.objects.bulk_create(events_to_create)

    created_events = list(Event.objects.all())
    registrations_to_create = []
    checkins_to_create = []
    
    for event in created_events:
        if event.status == Event.Status.APPROVED:
            # Create a CheckInSession
            if not CheckInSession.objects.filter(event=event).exists():
                checkins_to_create.append(CheckInSession(
                    event=event,
                    dynamic_code=f"qr_{event.id}_{uuid.uuid4().hex[:8]}",
                    expires_at=event.end_time
                ))
            
            # Register 5-15 random students
            for student in random.sample(students, k=min(len(students), random.randint(5, 15))):
                if not EventRegistration.objects.filter(student=student, event=event).exists():
                    is_checked_in = random.choice([True, False])
                    registrations_to_create.append(EventRegistration(
                        student=student,
                        event=event,
                        status=EventRegistration.Status.REGISTERED,
                        is_checked_in=is_checked_in
                    ))
                    
    if checkins_to_create:
        CheckInSession.objects.bulk_create(checkins_to_create)
    if registrations_to_create:
        EventRegistration.objects.bulk_create(registrations_to_create)

    print("Events data seeded successfully.")
