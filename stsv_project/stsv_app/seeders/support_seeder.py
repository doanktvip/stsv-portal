from django.utils import timezone
from datetime import timedelta
import random
from stsv_app.models.support import Complaint, FacilityReport
from stsv_app.models.users import User


def seed_support():
    print("--- Seeding Support Data ---")
    now = timezone.now()
    students = list(User.objects.filter(role=User.Role.STUDENT, is_active=True))
    admins = list(User.objects.filter(role=User.Role.ORGOFFICER))
    
    if not students:
        return

    admin_user = admins[0] if admins else None

    # Complaints
    complaints_to_create = []
    print("Seeding Complaints...")
    for _ in range(50):
        student = random.choice(students)
        status = random.choice(Complaint.Status.choices)[0]
        priority = random.choice(Complaint.Priority.choices)[0]
        
        c = Complaint(
            reporter=student,
            title=f"Khiếu nại số {random.randint(100, 999)}",
            description="Mô tả chi tiết khiếu nại...",
            priority=priority,
            status=status,
            admin_response="Đã tiếp nhận và xử lý." if status != Complaint.Status.PENDING else "",
            resolved_by=admin_user if status == Complaint.Status.CLOSED else None,
        )
        # Modify created_at later if needed, since it might be auto_now_add
        complaints_to_create.append(c)
        
    if complaints_to_create:
        Complaint.objects.bulk_create(complaints_to_create)

    # Facility Reports
    reports_to_create = []
    print("Seeding Facility Reports...")
    rooms = ["A1-101", "B2-202", "C1-304", "D1-401", "Kí túc xá", "Nhà ăn"]
    for _ in range(30):
        student = random.choice(students)
        status = random.choice(FacilityReport.Status.choices)[0]
        priority = random.choice(FacilityReport.Priority.choices)[0]
        
        r = FacilityReport(
            reporter=student,
            room=random.choice(rooms),
            description="Mô tả cơ sở vật chất bị hỏng...",
            priority=priority,
            status=status,
            resolved_by=admin_user if status == FacilityReport.Status.RESOLVED else None,
            image="https://dummyimage.com/400x300/000/fff.jpg&text=Facility" if random.random() > 0.5 else "",
            resolution_image="https://dummyimage.com/400x300/0f0/fff.jpg&text=Fixed" if status == FacilityReport.Status.RESOLVED else ""
        )
        reports_to_create.append(r)
        
    if reports_to_create:
        FacilityReport.objects.bulk_create(reports_to_create)

    print("Support data seeded successfully.")
