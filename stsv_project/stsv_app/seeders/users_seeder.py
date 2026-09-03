from django.utils import timezone
from datetime import timedelta
import random
import secrets
from django.contrib.auth.hashers import make_password
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile, UserDevice
from stsv_app.models.core import Faculty, Major, Cohort, HomeroomClass

vietnamese_first_names = ["Anh", "Bảo", "Bình", "Cường", "Châu", "Dũng", "Dương", "Đạt", "Giang", "Hải", "Hương", "Huy", "Hoa", "Hùng", "Khánh", "Lan", "Linh", "Minh", "Nam", "Nga", "Ngọc", "Phong", "Phúc", "Quang", "Quyên", "Sơn", "Trang", "Thảo", "Tuấn", "Thanh", "Vinh", "Vy", "Yến"]
vietnamese_last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]

def seed_users(num_students=50):
    print("--- Seeding Users Data ---")
    now = timezone.now()
    
    faculties = list(Faculty.objects.all())
    majors = list(Major.objects.all())
    cohorts = list(Cohort.objects.all())
    classes = list(HomeroomClass.objects.all())

    if not faculties or not majors or not cohorts or not classes:
        print("Missing core data (Faculty, Major, Cohort, Class). Skipping users.")
        return

    # Admin / Org (Keep simple creation for Org, since there are only a few)
    org_username_map = {
        OrgProfile.OrgType.FACULTY: "org_khoa",
        OrgProfile.OrgType.YOUTH_UNION_ASSOC: "org_doan_hoi",
        OrgProfile.OrgType.CLUB: "org_clb"
    }

    for org_type in OrgProfile.OrgType.choices:
        org_code = org_type[0]
        username = org_username_map.get(org_code, f"org_{org_code.lower()}")
        org_user, _ = User.objects.get_or_create(username=username, defaults={"role": User.Role.ORGOFFICER, "password": make_password("123456")})
        
        OrgProfile.objects.get_or_create(
            user=org_user, 
            defaults={
                "org_name": f"Tổ chức {org_code}",
                "org_type": org_code,
                "faculty": random.choice(faculties) if org_code == OrgProfile.OrgType.FACULTY else None,
                "status": OrgProfile.Status.ACTIVE,
                "established_date": (now - timedelta(days=365)).date()
            }
        )

    # Bulk create Lecturers
    print("Seeding Lecturers...")
    num_lecturers = 10
    lecturer_users = []
    pwd = make_password("123456")
    
    for i in range(num_lecturers):
        username = f"gv{i+1:02d}"
        if not User.objects.filter(username=username).exists():
            user = User(
                username=username,
                email=f"{username}@stsv.edu.vn",
                role=User.Role.LECTURER,
                password=pwd,
                first_name=random.choice(vietnamese_first_names),
                last_name=random.choice(vietnamese_last_names)
            )
            lecturer_users.append(user)
    
    if lecturer_users:
        User.objects.bulk_create(lecturer_users)
        created_lecturers = User.objects.filter(username__startswith='gv')
        lecturer_profiles = []
        for user in created_lecturers:
            if not LecturerProfile.objects.filter(user=user).exists():
                fac = random.choice(faculties)
                lecturer_profiles.append(LecturerProfile(
                    user=user,
                    lecturer_id=f"GV_{user.username}",
                    full_name=f"{user.last_name} {user.first_name}",
                    faculty=fac,
                    department=fac.name
                ))
        if lecturer_profiles:
            LecturerProfile.objects.bulk_create(lecturer_profiles)

    # Bulk create Students
    print(f"Seeding {num_students} Students...")
    student_users = []
    for i in range(num_students):
        username = f"sv{i+1:02d}"
        if not User.objects.filter(username=username).exists():
            # 85% Active, 15% Inactive
            is_active = random.random() < 0.85
            user = User(
                username=username,
                email=f"{username}@stsv.edu.vn",
                role=User.Role.STUDENT,
                password=pwd,
                is_active=is_active,
                first_name=random.choice(vietnamese_first_names),
                last_name=random.choice(vietnamese_last_names)
            )
            student_users.append(user)
            
    if student_users:
        # Create Users
        User.objects.bulk_create(student_users)
        
        # Query them back to get IDs
        created_users = User.objects.filter(role=User.Role.STUDENT).exclude(username='student_active').exclude(username='student_inactive')
        
        student_profiles = []
        user_devices = []
        
        for user in created_users:
            if not StudentProfile.objects.filter(user=user).exists():
                hc = random.choice(classes)
                student_profiles.append(StudentProfile(
                    user=user,
                    student_id=user.username.upper(),
                    full_name=f"{user.last_name} {user.first_name}",
                    faculty=hc.major.faculty,
                    major=hc.major,
                    cohort=hc.cohort,
                    homeroom_class=hc
                ))
                
                # Assign devices to active students mostly
                if user.is_active and random.random() < 0.8:
                    os_choice = random.choice(UserDevice.OS.choices)[0]
                    user_devices.append(UserDevice(
                        user=user,
                        fcm_token=secrets.token_hex(10),
                        device_os=os_choice
                    ))
                    
        if student_profiles:
            StudentProfile.objects.bulk_create(student_profiles)
        if user_devices:
            UserDevice.objects.bulk_create(user_devices)

    print("Users data seeded successfully.")
