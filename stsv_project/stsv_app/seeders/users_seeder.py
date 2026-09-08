import random
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from stsv_app.models import User, StudentProfile, OrgProfile, Faculty, HomeroomClass

vietnamese_first_names = ["Anh", "Bảo", "Bình", "Cường", "Châu", "Dũng", "Dương", "Đạt", "Giang", "Hải", "Hương", "Huy", "Hoa", "Hùng", "Khánh", "Lan", "Linh", "Minh", "Nam", "Nga", "Ngọc", "Phong", "Phúc", "Quang", "Quyên", "Sơn", "Trang", "Thảo", "Tuấn", "Thanh", "Vinh", "Vy", "Yến"]
vietnamese_last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]

def seed_users(num_students=50):
    print("--- Nạp Dữ Liệu Tài Khoản & Người Dùng ---")
    now = timezone.now()
    
    faculties = list(Faculty.objects.all())
    classes = list(HomeroomClass.objects.all())

    if not faculties or not classes:
        print("Thiếu dữ liệu cốt lõi (Khoa, Lớp). Bỏ qua nạp tài khoản.")
        return


    # Admin
    User.objects.get_or_create(username="admin", defaults={
        "role": User.Role.ADMIN, 
        "password": make_password("123456"),
        "is_superuser": True,
        "is_staff": True
    })

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

    # Bulk create Students
    print(f"Đang nạp {num_students} Sinh viên...")
    student_users = []
    pwd = make_password("123456")
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
        
        for user in created_users:
            if not StudentProfile.objects.filter(user=user).exists():
                hc = random.choice(classes)
                student_profiles.append(StudentProfile(
                    user=user,
                    student_id=user.username.upper(),
                    full_name=f"{user.last_name} {user.first_name}",
                    faculty=hc.faculty,
                    cohort_year=hc.cohort_year,
                    homeroom_class=hc
                ))
                

        if student_profiles:
            StudentProfile.objects.bulk_create(student_profiles)

        # Set BANCANSU (President) for each class
        for hc in classes:
            students_in_class = StudentProfile.objects.filter(homeroom_class=hc)
            if students_in_class.exists():
                president_profile = random.choice(list(students_in_class))
                hc.president = president_profile
                hc.save()
                
                president_user = president_profile.user
                president_user.role = User.Role.BANCANSU
                president_user.save()


    print("Nạp dữ liệu tài khoản & người dùng thành công.")

