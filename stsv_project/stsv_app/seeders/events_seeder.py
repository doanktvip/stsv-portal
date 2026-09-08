import random
import uuid
from django.utils import timezone
from datetime import timedelta
from stsv_app.models import EventCategory, Event, CheckInSession, EventRegistration, OrgProfile, StudentProfile, TrainingCriterion


def seed_events(num_events=20):
    print("--- Nạp Dữ Liệu Sự Kiện ---")
    now = timezone.now()
    
    # Xóa sự kiện cũ để dọn dẹp
    Event.objects.all().delete()
    
    cats_data = [
        ("Hội thảo khoa học", "Điều 1"),
        ("Hoạt động tình nguyện", "Điều 4"),
        ("Văn hóa, Văn nghệ", "Điều 3"),
        ("Giao lưu quốc tế", "Điều 3"),
    ]
    
    categories = []
    for c_name, c_crit in cats_data:
        criterion, _ = TrainingCriterion.objects.get_or_create(name=c_crit)
        cat, _ = EventCategory.objects.get_or_create(name=c_name, defaults={"criterion": criterion})
        if cat.criterion != criterion:
            cat.criterion = criterion
            cat.save()
        categories.append(cat)
        
    orgs = list(OrgProfile.objects.all())
    students = list(StudentProfile.objects.all())
    if not orgs or not students:
        print("Thiếu thông tin Ban tổ chức hoặc Sinh viên. Bỏ qua nạp sự kiện.")
        return

    events_to_create = []
    
    # Generate bulk events
    print(f"Đang nạp {num_events} Sự kiện...")

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
            category=random.choice(categories),
            organizer=org,
            start_time=start_time,
            end_time=end_time,
            location=f"Hội trường {random.choice(['A', 'B', 'C'])}",
            capacity=random.randint(50, 100),
            waitlist_capacity=random.randint(10, 50),
            point_reward=random.randint(3, 5),
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
                    status = random.choice(EventRegistration.Status.choices)[0]
                    registrations_to_create.append(EventRegistration(
                        student=student,
                        event=event,
                        status=status,
                    ))
                    
    if checkins_to_create:
        CheckInSession.objects.bulk_create(checkins_to_create)
    if registrations_to_create:
        EventRegistration.objects.bulk_create(registrations_to_create)

    print("Nạp dữ liệu sự kiện thành công.")

