import os
import django

# Thiết lập môi trường Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stsv_project.settings")
django.setup()

import random
from datetime import date, time
from decimal import Decimal
from django.db import transaction
from django.core.management import call_command
from stsv_app.models.core import Faculty, Major, Cohort, HomeroomClass
from stsv_app.models.academics import (
    GradeConversionRule,
    Semester,
    Subject,
    EducationProgram,
    CourseClass,
    ScoreComponent,
    StudentCourse,
    StudentScoreDetail,
    Schedule,
)
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from stsv_app.models.events import EventCategory, Event, CheckInSession, EventRegistration, YouthUnionRecord
from stsv_app.models.training_points import TrainingCriterion, StudentSemesterPoint, SemesterPointDetail, PointProof, \
    PointHistory
from stsv_app.models.academics import StudentSemesterSummary, IntegrationSyncLog
from stsv_app.models.finance import Fee, Payment
from stsv_app.models.support import FacilityReport, Complaint
from stsv_app.models.system import SystemConfig, NotificationTemplate, UserNotification
from stsv_app.models.users import UserDevice

faculties_data = [
    {
        "code": "CNTT",
        "name": "Khoa Công nghệ thông tin",
        "majors": [
            {"code": "7480101", "name": "Khoa học máy tính"},
            {"code": "7480201", "name": "Công nghệ thông tin"},
        ],
    },
    {
        "code": "XD",
        "name": "Khoa Xây dựng",
        "majors": [
            {"code": "7510102", "name": "Công nghệ kỹ thuật công trình xây dựng"},
            {"code": "7510103", "name": "Quản lý xây dựng"},
        ],
    },
]

cohorts_data = [
    {"code": "K25", "enrollment_year": 2025},
    {"code": "K26", "enrollment_year": 2026},
    {"code": "K27", "enrollment_year": 2027},
]

grade_conversion_rules_data = [
    {
        "min": Decimal("9.0"),
        "max": Decimal("10.0"),
        "letter": "A+",
        "score4": Decimal("4.0"),
        "classification": "PASS",
    },
    {
        "min": Decimal("8.5"),
        "max": Decimal("8.9"),
        "letter": "A",
        "score4": Decimal("4.0"),
        "classification": "PASS",
    },
    {
        "min": Decimal("8.0"),
        "max": Decimal("8.4"),
        "letter": "B+",
        "score4": Decimal("3.5"),
        "classification": "PASS",
    },
    {
        "min": Decimal("7.0"),
        "max": Decimal("7.9"),
        "letter": "B",
        "score4": Decimal("3.0"),
        "classification": "PASS",
    },
    {
        "min": Decimal("6.5"),
        "max": Decimal("6.9"),
        "letter": "C+",
        "score4": Decimal("2.5"),
        "classification": "PASS",
    },
    {
        "min": Decimal("5.5"),
        "max": Decimal("6.4"),
        "letter": "C",
        "score4": Decimal("2.0"),
        "classification": "PASS",
    },
    {
        "min": Decimal("5.0"),
        "max": Decimal("5.4"),
        "letter": "D+",
        "score4": Decimal("1.5"),
        "classification": "PASS",
    },
    {
        "min": Decimal("4.0"),
        "max": Decimal("4.9"),
        "letter": "D",
        "score4": Decimal("1.0"),
        "classification": "PASS",
    },
    {
        "min": Decimal("0.0"),
        "max": Decimal("3.9"),
        "letter": "F",
        "score4": Decimal("0.0"),
        "classification": "FAIL",
    },
]


def seed_faculties_and_majors():
    print("--- Bắt đầu tạo dữ liệu Khoa và Ngành ---")
    created_faculties_count = 0
    created_majors_count = 0

    for data in faculties_data:
        faculty, created = Faculty.objects.get_or_create(code=data["code"], defaults={"name": data["name"]})
        if created:
            print(f"Đã tạo Khoa: {faculty.code} - {faculty.name}")
            created_faculties_count += 1
        else:
            if faculty.name != data["name"]:
                faculty.name = data["name"]
                faculty.save()
                print(f"Đã cập nhật Khoa: {faculty.code} - {faculty.name}")

        for major_data in data["majors"]:
            major, m_created = Major.objects.get_or_create(
                code=major_data["code"],
                defaults={"name": major_data["name"], "faculty": faculty},
            )
            if m_created:
                print(f"  + Đã tạo Ngành: {major.code} - {major.name}")
                created_majors_count += 1
            else:
                updated = False
                if major.name != major_data["name"]:
                    major.name = major_data["name"]
                    updated = True
                if major.faculty != faculty:
                    major.faculty = faculty
                    updated = True

                if updated:
                    major.save()
                    print(f"  + Đã cập nhật Ngành: {major.code} - {major.name}")

    print(f"-> Đã tạo mới {created_faculties_count} Khoa và {created_majors_count} Ngành.\n")


def seed_cohorts():
    print("--- Bắt đầu tạo dữ liệu Khóa học (Cohort) ---")
    created_count = 0
    for data in cohorts_data:
        obj, created = Cohort.objects.get_or_create(
            code=data["code"], defaults={"enrollment_year": data["enrollment_year"]}
        )
        if created:
            print(f"Đã tạo: {obj.code} - Năm nhập học: {obj.enrollment_year}")
            created_count += 1
        else:
            if obj.enrollment_year != data["enrollment_year"]:
                obj.enrollment_year = data["enrollment_year"]
                obj.save()
                print(f"Đã cập nhật: {obj.code} - Năm nhập học: {obj.enrollment_year}")
            else:
                print(f"Đã tồn tại: {obj.code} - Năm nhập học: {obj.enrollment_year}")

    print(f"-> Đã tạo mới {created_count} Khóa học.\n")


def seed_grade_conversion_rules():
    print("--- Bắt đầu tạo dữ liệu Quy tắc đổi điểm (GradeConversionRule) ---")
    created_count = 0
    for data in grade_conversion_rules_data:
        rule, created = GradeConversionRule.objects.get_or_create(
            letter_grade=data["letter"],
            defaults={
                "min_score_10": data["min"],
                "max_score_10": data["max"],
                "score_4": data["score4"],
                "classification": data["classification"],
            },
        )
        if created:
            print(f"Đã tạo: {rule.letter_grade} ({rule.min_score_10} - {rule.max_score_10}) -> {rule.score_4}")
            created_count += 1
        else:
            updated = False
            if rule.min_score_10 != data["min"]:
                rule.min_score_10 = data["min"]
                updated = True
            if rule.max_score_10 != data["max"]:
                rule.max_score_10 = data["max"]
                updated = True
            if rule.score_4 != data["score4"]:
                rule.score_4 = data["score4"]
                updated = True
            if rule.classification != data["classification"]:
                rule.classification = data["classification"]
                updated = True

            if updated:
                rule.save()
                print(f"Đã cập nhật: {rule.letter_grade}")
            else:
                print(f"Đã tồn tại: {rule.letter_grade}")

    print(f"-> Đã tạo mới {created_count} quy tắc đổi điểm.\n")


semesters_data = [
    {"code": "20251", "start_date": date(2025, 9, 5), "end_date": date(2026, 1, 15)},
    {"code": "20252", "start_date": date(2026, 2, 15), "end_date": date(2026, 6, 15)},
    {"code": "20253", "start_date": date(2026, 6, 25), "end_date": date(2026, 8, 15)},
    {"code": "20261", "start_date": date(2026, 9, 5), "end_date": date(2027, 1, 15)},
    {"code": "20262", "start_date": date(2027, 2, 15), "end_date": date(2027, 6, 15)},
    {"code": "20263", "start_date": date(2027, 6, 25), "end_date": date(2027, 8, 15)},
    {"code": "20271", "start_date": date(2027, 9, 5), "end_date": date(2028, 1, 15)},
    {"code": "20272", "start_date": date(2028, 2, 15), "end_date": date(2028, 6, 15)},
    {"code": "20273", "start_date": date(2028, 6, 25), "end_date": date(2028, 8, 15)},
    {"code": "20281", "start_date": date(2028, 9, 5), "end_date": date(2029, 1, 15)},
    {"code": "20282", "start_date": date(2029, 2, 15), "end_date": date(2029, 6, 15)},
    {"code": "20283", "start_date": date(2029, 6, 25), "end_date": date(2029, 8, 15)},
    {"code": "20291", "start_date": date(2029, 9, 5), "end_date": date(2030, 1, 15)},
    {"code": "20292", "start_date": date(2030, 2, 15), "end_date": date(2030, 6, 15)},
    {"code": "20293", "start_date": date(2030, 6, 25), "end_date": date(2030, 8, 15)},
]

subjects_data = [
    # CNTT
    {
        "code": "IT001",
        "name": "Nhập môn lập trình",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT011",
        "name": "Toán rời rạc",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT004",
        "name": "Mạng máy tính",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT012",
        "name": "Kiến trúc máy tính",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT002",
        "name": "Cấu trúc dữ liệu và giải thuật",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": ["IT001"],
    },
    {
        "code": "IT013",
        "name": "Cơ sở dữ liệu",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT005",
        "name": "Hệ điều hành",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": ["IT012"],
    },
    {
        "code": "IT014",
        "name": "Phân tích thiết kế hệ thống",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT015",
        "name": "Lập trình hướng đối tượng",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "IT016",
        "name": "Mật mã học cơ sở",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "CS003",
        "name": "Đồ họa máy tính",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "CS011",
        "name": "Thị giác máy tính",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "CS001",
        "name": "Trí tuệ nhân tạo",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": ["IT002"],
    },
    {
        "code": "CS012",
        "name": "Xử lý ảnh số",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "CS002",
        "name": "Học máy",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": ["CS001"],
    },
    {
        "code": "CS013",
        "name": "Xử lý ngôn ngữ tự nhiên",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "CS014",
        "name": "Chuyên đề Khoa học máy tính",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "CS099",
        "name": "Đồ án tốt nghiệp KHMT",
        "credits": 6,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE001",
        "name": "Công nghệ phần mềm",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE011",
        "name": "Kiểm thử phần mềm",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE002",
        "name": "Phát triển ứng dụng Web",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": ["IT013"],
    },
    {
        "code": "SE012",
        "name": "Thiết kế giao diện UI/UX",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE015",
        "name": "Thiết kế trải nghiệm người dùng",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE003",
        "name": "Phát triển ứng dụng Di động",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": ["IT001"],
    },
    {
        "code": "SE013",
        "name": "Kiến trúc phần mềm",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE014",
        "name": "Chuyên đề Công nghệ thông tin",
        "credits": 3,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    {
        "code": "SE099",
        "name": "Đồ án tốt nghiệp CNTT",
        "credits": 6,
        "faculty_code": "CNTT",
        "prereqs": [],
    },
    # XD
    {
        "code": "CE001",
        "name": "Cơ học cơ sở",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE011",
        "name": "Hình họa - Vẽ kỹ thuật",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE003",
        "name": "Vật liệu xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE012",
        "name": "Kiến trúc dân dụng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE002",
        "name": "Sức bền vật liệu",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": ["CE001"],
    },
    {
        "code": "CE013",
        "name": "Thủy lực cơ sở",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE004",
        "name": "Trắc địa",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE014",
        "name": "Cơ học kết cấu",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CE005",
        "name": "Cơ học đất",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": ["CE002"],
    },
    {
        "code": "CE015",
        "name": "Máy xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CT001",
        "name": "Kỹ thuật thi công",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CT011",
        "name": "Kết cấu thép",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CT002",
        "name": "Kết cấu bê tông cốt thép",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": ["CE002"],
    },
    {
        "code": "CT012",
        "name": "Động đất và chống động đất",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CT003",
        "name": "Nền móng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": ["CE005"],
    },
    {
        "code": "CT013",
        "name": "Thi công cầu đường",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CT014",
        "name": "Chuyên đề Kỹ thuật Xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CT099",
        "name": "Đồ án tốt nghiệp KTXD",
        "credits": 6,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM001",
        "name": "Kinh tế xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM011",
        "name": "Kế toán xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM004",
        "name": "Luật xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM012",
        "name": "Định giá xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM002",
        "name": "Lập dự toán",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": ["CM001"],
    },
    {
        "code": "CM013",
        "name": "Quản lý chất lượng dự án",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM014",
        "name": "Chuyên đề Quản lý Xây dựng",
        "credits": 3,
        "faculty_code": "XD",
        "prereqs": [],
    },
    {
        "code": "CM099",
        "name": "Đồ án tốt nghiệp QLXD",
        "credits": 6,
        "faculty_code": "XD",
        "prereqs": [],
    },
]

education_programs_data = []
cohorts_list = [c["code"] for c in cohorts_data]

training_criteria_data = [
    {
        "code": "TC1",
        "name": "Trách nhiệm chấp hành pháp luật và nội quy, quy chế của nhà trường",
        "max_points": 25,
    },
    {
        "code": "TC2",
        "name": "Trách nhiệm, tinh thần và thái độ trong học tập",
        "max_points": 20,
    },
    {
        "code": "TC3",
        "name": "Trách nhiệm tham gia các hoạt động chính trị - xã hội, văn hóa, văn nghệ, thể thao, phòng chống tội phạm, tệ nạn xã hội",
        "max_points": 20,
    },
    {
        "code": "TC4",
        "name": "Trách nhiệm công dân trong quan hệ cộng đồng",
        "max_points": 15,
    },
    {
        "code": "TC5",
        "name": "Đánh giá về ý thức và kết quả tham gia phụ trách lớp học, các đoàn thể, tổ chức khác trong nhà trường",
        "max_points": 20,
    },
    {
        "code": "TC6",
        "name": "Các trường hợp đặc biệt",
        "max_points": 10,
    },
]


def add_prog(major_code, cohort_code, semester, subjects):
    for sub in subjects:
        education_programs_data.append(
            {
                "major_code": major_code,
                "cohort_code": cohort_code,
                "subject_code": sub,
                "semester": semester,
                "is_mandatory": True,
            }
        )


for cohort in cohorts_list:
    # --- KHOA CÔNG NGHỆ THÔNG TIN ---
    # Các môn cơ sở ngành chung cho cả 7480101 (KHMT) và 7480201 (CNTT)
    for major in ["7480101", "7480201"]:
        add_prog(major, cohort, 1, ["IT001", "IT011"])
        add_prog(major, cohort, 2, ["IT004", "IT012"])
        add_prog(major, cohort, 3, ["IT002", "IT013"])
        add_prog(major, cohort, 4, ["IT005", "IT014"])
        add_prog(major, cohort, 5, ["IT015", "IT016"])

    # Chuyên ngành KHMT (7480101)
    if cohort == "K25":
        add_prog("7480101", cohort, 6, ["CS003", "CS011"])
        add_prog("7480101", cohort, 7, ["CS001", "CS012"])
    elif cohort == "K26":
        add_prog("7480101", cohort, 6, ["CS011", "CS014"])
        add_prog("7480101", cohort, 7, ["CS001", "CS012"])
    elif cohort == "K27":
        add_prog("7480101", cohort, 6, ["CS003", "CS011"])
        add_prog("7480101", cohort, 7, ["CS001", "CS013"])
    add_prog("7480101", cohort, 8, ["CS002", "CS013"])
    add_prog("7480101", cohort, 9, ["CS014", "CS099"])

    # Chuyên ngành CNTT (7480201)
    if cohort == "K25":
        add_prog("7480201", cohort, 6, ["SE001", "SE011"])
        add_prog("7480201", cohort, 7, ["SE002", "SE012"])
        add_prog("7480201", cohort, 8, ["SE003", "SE013"])
    elif cohort == "K26":
        add_prog("7480201", cohort, 6, ["SE001", "SE011"])
        add_prog("7480201", cohort, 7, ["SE002", "SE015"])
        add_prog("7480201", cohort, 8, ["SE003", "SE013"])
    elif cohort == "K27":
        add_prog("7480201", cohort, 6, ["SE001", "SE011"])
        add_prog("7480201", cohort, 7, ["SE003", "SE012"])
        add_prog("7480201", cohort, 8, ["SE002", "SE013"])
    add_prog("7480201", cohort, 9, ["SE014", "SE099"])

    # --- KHOA XÂY DỰNG ---
    # Các môn cơ sở ngành chung cho cả 7510102 (KTXD) và 7510103 (QLXD)
    for major in ["7510102", "7510103"]:
        add_prog(major, cohort, 1, ["CE001", "CE011"])
        add_prog(major, cohort, 2, ["CE003", "CE012"])
        add_prog(major, cohort, 3, ["CE002", "CE013"])
        add_prog(major, cohort, 4, ["CE004", "CE014"])
        add_prog(major, cohort, 5, ["CE005", "CE015"])

    # Chuyên ngành Công nghệ KT Công trình xây dựng (7510102)
    add_prog("7510102", cohort, 6, ["CT001", "CT011"])
    add_prog("7510102", cohort, 7, ["CT002", "CT012"])
    if cohort == "K25":
        add_prog("7510102", cohort, 8, ["CT003", "CT013"])
        add_prog("7510102", cohort, 9, ["CT014", "CT099"])
    elif cohort == "K26":
        add_prog("7510102", cohort, 8, ["CT003", "CT014"])
        add_prog("7510102", cohort, 9, ["CT013", "CT099"])  # Đổi chỗ CT013 và CT014
    elif cohort == "K27":
        add_prog("7510102", cohort, 8, ["CT013", "CT014"])
        add_prog("7510102", cohort, 9, ["CT003", "CT099"])

    # Chuyên ngành Quản lý Xây dựng (7510103)
    add_prog("7510103", cohort, 6, ["CM001", "CM011"])
    add_prog("7510103", cohort, 7, ["CM004", "CM012"])
    add_prog("7510103", cohort, 8, ["CM002", "CM013"])
    if cohort == "K25":
        add_prog("7510103", cohort, 9, ["CM014", "CM099"])
    else:
        add_prog("7510103", cohort, 9, ["CM013", "CM099"])


def seed_semesters():
    print("--- Bắt đầu tạo dữ liệu Học kỳ (Semester) ---")
    created_count = 0
    for data in semesters_data:
        obj, created = Semester.objects.get_or_create(
            code=data["code"],
            defaults={"start_date": data["start_date"], "end_date": data["end_date"]},
        )
        if created:
            created_count += 1
        else:
            if obj.start_date != data["start_date"] or obj.end_date != data["end_date"]:
                obj.start_date = data["start_date"]
                obj.end_date = data["end_date"]
                obj.save()
    print(f"-> Đã tạo mới {created_count} Học kỳ.\n")


def seed_subjects():
    print("--- Bắt đầu tạo dữ liệu Môn học (Subject) ---")
    created_count = 0
    for data in subjects_data:
        faculty = Faculty.objects.get(code=data["faculty_code"])
        obj, created = Subject.objects.get_or_create(
            subject_code=data["code"],
            defaults={
                "name": data["name"],
                "credits": data["credits"],
                "faculty": faculty,
            },
        )
        if created:
            created_count += 1
        else:
            if obj.name != data["name"] or obj.credits != data["credits"] or obj.faculty != faculty:
                obj.name = data["name"]
                obj.credits = data["credits"]
                obj.faculty = faculty
                obj.save()

    for data in subjects_data:
        obj = Subject.objects.get(subject_code=data["code"])
        prereqs = []
        for p_code in data["prereqs"]:
            p_obj = Subject.objects.get(subject_code=p_code)
            prereqs.append(p_obj)
        if prereqs:
            obj.prerequisite_subjects.set(prereqs)

    print(f"-> Đã tạo/cập nhật {len(subjects_data)} Môn học (tạo mới {created_count}).\n")


def seed_education_programs():
    print("--- Bắt đầu tạo dữ liệu Chương trình đào tạo (EducationProgram) ---")
    created_count = 0
    for data in education_programs_data:
        major = Major.objects.get(code=data["major_code"])
        cohort = Cohort.objects.get(code=data["cohort_code"])
        subject = Subject.objects.get(subject_code=data["subject_code"])

        obj, created = EducationProgram.objects.get_or_create(
            major=major,
            cohort=cohort,
            subject=subject,
            defaults={
                "recommended_semester": data["semester"],
                "is_mandatory": data["is_mandatory"],
            },
        )
        if created:
            created_count += 1
        else:
            if obj.recommended_semester != data["semester"] or obj.is_mandatory != data["is_mandatory"]:
                obj.recommended_semester = data["semester"]
                obj.is_mandatory = data["is_mandatory"]
                obj.save()

    print(f"-> Đã tạo mới/cập nhật {len(education_programs_data)} bản ghi CTĐT (tạo mới {created_count}).\n")


def seed_users():
    print("--- Bắt đầu tạo dữ liệu Tài khoản (Users) ---")

    # 1. Tạo ADMIN theo yêu cầu mới
    PASSWORD = "123456"
    if not User.objects.filter(username="admin").exists():
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password=PASSWORD,
            role="ADMIN",
            first_name="Đoàn",
            last_name="Nguyễn Văn",
        )
        print(f"Đã tạo Admin: {admin.username}/{PASSWORD}")
    else:
        print("Admin admin đã tồn tại.")

    last_names = [
        "Nguyễn",
        "Trần",
        "Lê",
        "Phạm",
        "Hoàng",
        "Huỳnh",
        "Phan",
        "Vũ",
        "Võ",
        "Đặng",
    ]
    middle_names = [
        "Văn",
        "Thị",
        "Thanh",
        "Minh",
        "Hữu",
        "Đức",
        "Ngọc",
        "Thu",
        "Xuân",
        "Hải",
    ]
    first_names = [
        "Anh",
        "Bình",
        "Châu",
        "Dũng",
        "Hoa",
        "Khoa",
        "Linh",
        "Nam",
        "Oanh",
        "Phong",
        "Quân",
        "Trang",
        "Tùng",
        "Vy",
    ]

    def get_random_name_parts():
        return random.choice(last_names), random.choice(middle_names), random.choice(first_names)

    faculties = Faculty.objects.all()

    # 2. Tạo 5 ORGOFFICER
    org_count = 0
    # - 2 tài khoản khoa
    for i, faculty in enumerate(faculties):
        username = "giaovu" if i == 0 else f"giaovu_{faculty.code.lower()}"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(PASSWORD)
            user.role = User.Role.ORGOFFICER
            user.first_name = "Giáo vụ"
            user.last_name = faculty.name
            user.email = f"{username}@stsv.edu.vn"
            user.save()
            OrgProfile.objects.create(
                user=user,
                org_name=f"Giáo vụ {faculty.name}",
                org_type=OrgProfile.OrgType.FACULTY,
                faculty=faculty,
            )
            org_count += 1

    # - 2 tài khoản CLB
    club_names = ["CLB Âm nhạc", "CLB IT"]
    for i, club_name in enumerate(club_names):
        username = "clb" if i == 0 else f"clb_{i + 1}"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(PASSWORD)
            user.role = User.Role.ORGOFFICER
            user.first_name = "Ban"
            user.last_name = "Chủ nhiệm"
            user.email = f"{username}@stsv.edu.vn"
            user.save()
            OrgProfile.objects.create(user=user, org_name=club_name, org_type=OrgProfile.OrgType.CLUB)
            org_count += 1

    # - 1 tài khoản Đoàn Hội
    doanhoi_user, dh_created = User.objects.get_or_create(username="doanhoi")
    if dh_created:
        doanhoi_user.set_password(PASSWORD)
        doanhoi_user.role = User.Role.ORGOFFICER
        doanhoi_user.first_name = "Bí thư"
        doanhoi_user.last_name = "Đoàn"
        doanhoi_user.email = "doanhoi@stsv.edu.vn"
        doanhoi_user.save()
        OrgProfile.objects.create(
            user=doanhoi_user,
            org_name="Đoàn Thanh niên - Hội Sinh viên",
            org_type=OrgProfile.OrgType.YOUTH_UNION_ASSOC,
        )
        org_count += 1

    print(f"Đã tạo {org_count} Cán bộ Tổ chức.")

    # 3. Tạo LECTURER (8 giảng viên, mỗi khoa 4)
    lecturer_count = 0
    lecturers_list = []
    is_first_lecturer = True
    for faculty in faculties:
        for i in range(1, 5):  # 4 giảng viên
            if is_first_lecturer:
                lecturer_id = "gv"
                is_first_lecturer = False
            else:
                lecturer_id = f"GV_{faculty.code}_{i:02d}"
            user, created = User.objects.get_or_create(username=lecturer_id)
            if created:
                l, m, f = get_random_name_parts()
                user.set_password(PASSWORD)
                user.role = User.Role.LECTURER
                user.first_name = f
                user.last_name = f"{l} {m}"
                user.email = f"{lecturer_id.lower()}@stsv.edu.vn"
                user.save()
                lp = LecturerProfile.objects.create(
                    user=user,
                    lecturer_id=lecturer_id,
                    full_name=f"{l} {m} {f}",
                    faculty=faculty,
                    department=faculty.name,
                )
                lecturers_list.append(lp)
                lecturer_count += 1
            else:
                lecturers_list.append(user.lecturer_profile)
    print(f"Đã tạo {lecturer_count} Giảng viên.")

    # 4. Tạo STUDENT và HomeroomClass
    student_count = 0
    target_cohorts = Cohort.objects.filter(code__in=["K25", "K26"])
    majors = Major.objects.all()
    homeroom_classes = []
    is_first_student = True

    for major in majors:
        for cohort in target_cohorts:
            class_name = f"{cohort.code}_{major.code}_1"
            advisor = random.choice(
                [l for l in lecturers_list if l.faculty_id == major.faculty_id]) if lecturers_list else None
            hc, hc_created = HomeroomClass.objects.get_or_create(
                name=class_name,
                defaults={
                    "major": major,
                    "cohort": cohort,
                    "advisor": advisor
                }
            )
            homeroom_classes.append(hc)

            class_students = []
            for i in range(1, 6):  # 5 sinh viên
                if is_first_student:
                    student_id = "sv"
                    is_first_student = False
                else:
                    student_id = f"{cohort.code}_{major.code}_{i:02d}"
                user, created = User.objects.get_or_create(username=student_id)
                if created:
                    l, m, f = get_random_name_parts()
                    user.set_password(PASSWORD)
                    user.role = User.Role.STUDENT
                    user.first_name = f
                    user.last_name = f"{l} {m}"
                    user.email = f"{student_id.lower()}@stsv.edu.vn"
                    user.save()
                    sp = StudentProfile.objects.create(
                        user=user,
                        student_id=student_id,
                        full_name=f"{l} {m} {f}",
                        faculty=major.faculty,
                        major=major,
                        cohort=cohort,
                        homeroom_class=hc,
                    )
                    class_students.append(sp)
                    student_count += 1
                else:
                    class_students.append(user.student_profile)

            if hc and class_students and not hc.president:
                hc.president = random.choice(class_students)
                hc.save()

    print(f"Đã tạo {student_count} Sinh viên và {len(homeroom_classes)} Lớp sinh hoạt.")
    print("-> Đã hoàn tất tạo tài khoản.\n")


def seed_classes_and_scores():
    print("--- Bắt đầu tạo dữ liệu Lớp học phần, Lịch học & Điểm số (Classes & Scores) ---")

    # 1. Tạo ScoreComponent cho tất cả Subject
    subjects = Subject.objects.all()
    for subject in subjects:
        ScoreComponent.objects.get_or_create(subject=subject, name="Chuyên cần", defaults={"weight_percentage": 10})
        ScoreComponent.objects.get_or_create(subject=subject, name="Giữa kỳ", defaults={"weight_percentage": 30})
        ScoreComponent.objects.get_or_create(subject=subject, name="Cuối kỳ", defaults={"weight_percentage": 60})

    # K25 cohorts and their target semesters
    k25_cohort = Cohort.objects.get(code="K25")
    semesters_map = {
        1: Semester.objects.get(code="20251"),
        2: Semester.objects.get(code="20252"),
        3: Semester.objects.get(code="20253")
    }

    grade_rules = GradeConversionRule.objects.all().order_by('-min_score_10')

    def calculate_grade(total_10):
        if total_10 is None:
            return None, None, None
        for rule in grade_rules:
            if rule.min_score_10 <= total_10 <= rule.max_score_10:
                return rule.score_4, rule.letter_grade, rule.classification == GradeConversionRule.Classification.PASS
        return Decimal("0.0"), "F", False

    lecturers_by_faculty = {}
    for faculty in Faculty.objects.all():
        lecturers_by_faculty[faculty.id] = list(LecturerProfile.objects.filter(faculty=faculty))

    rooms = ["A1-101", "A1-102", "A1-201", "B2-101", "B2-205", "C1-301"]
    days = [2, 3, 4, 5, 6, 7]
    time_slots = [
        (time(7, 0), time(9, 30)),
        (time(9, 30), time(12, 0)),
        (time(13, 0), time(15, 30)),
        (time(15, 30), time(18, 0))
    ]

    class_count = 0
    score_count = 0

    with transaction.atomic():
        # Lặp qua các học kỳ 1, 2, 3 của K25
        for rec_sem, semester in semesters_map.items():
            ep_list = EducationProgram.objects.filter(cohort=k25_cohort, recommended_semester=rec_sem)

            # Gom nhóm môn học theo Khoa để mở lớp
            subject_faculty_map = {}
            for ep in ep_list:
                key = (ep.subject_id, ep.major.faculty_id)
                if key not in subject_faculty_map:
                    subject_faculty_map[key] = []
                subject_faculty_map[key].append(ep.major_id)

            for (subject_id, faculty_id), major_ids in subject_faculty_map.items():
                subject = Subject.objects.get(id=subject_id)
                faculty = Faculty.objects.get(id=faculty_id)

                # Mở Lớp học phần
                class_code = f"{subject.subject_code}_{semester.code}_{faculty.code}01"
                lecturer = random.choice(lecturers_by_faculty[faculty.id]) if lecturers_by_faculty.get(
                    faculty.id) else None
                course_class, created = CourseClass.objects.get_or_create(
                    subject=subject,
                    semester=semester,
                    class_code=class_code,
                    defaults={
                        "lecturer": lecturer,
                        "capacity": 100
                    }
                )

                # Tạo Lịch học
                if created:
                    day = random.choice(days)
                    t_start, t_end = random.choice(time_slots)
                    room = random.choice(rooms)
                    Schedule.objects.create(
                        course_class=course_class,
                        type=Schedule.Type.CLASS,
                        day_of_week=day,
                        start_time=t_start,
                        end_time=t_end,
                        room=room
                    )
                    class_count += 1

                # Ghi danh sinh viên K25 & Chấm điểm
                students = StudentProfile.objects.filter(cohort=k25_cohort, major_id__in=major_ids)
                components = ScoreComponent.objects.filter(subject=subject)
                cc_comp = components.get(name="Chuyên cần")
                gk_comp = components.get(name="Giữa kỳ")
                ck_comp = components.get(name="Cuối kỳ")

                for student in students:
                    student_course, sc_created = StudentCourse.objects.get_or_create(
                        student=student,
                        course_class=course_class
                    )

                    if sc_created:
                        course_class.current_enrollment += 1

                        cc_score = Decimal(random.randint(70, 100)) / 10
                        gk_score = Decimal(random.randint(50, 100)) / 10

                        StudentScoreDetail.objects.create(student_course=student_course, score_component=cc_comp,
                                                          score_value=cc_score)
                        StudentScoreDetail.objects.create(student_course=student_course, score_component=gk_comp,
                                                          score_value=gk_score)

                        if rec_sem in [1, 2]:  # Các kỳ đã kết thúc (20251, 20252) có điểm thi cuối kỳ
                            ck_score = Decimal(random.randint(40, 100)) / 10
                            StudentScoreDetail.objects.create(student_course=student_course, score_component=ck_comp,
                                                              score_value=ck_score)

                            total_10 = (cc_score * 10 + gk_score * 30 + ck_score * 60) / 100
                            total_10 = round(total_10, 2)

                            score_4, letter_grade, is_passed = calculate_grade(total_10)
                            student_course.total_score_10 = total_10
                            student_course.total_score_4 = score_4
                            student_course.total_score_letter = letter_grade
                            student_course.is_passed = is_passed
                            student_course.save()
                        score_count += 1

                course_class.save()

    print(f"-> Đã mở {class_count} Lớp học phần kèm Lịch học, gán Điểm cho {score_count} sinh viên.\n")


def seed_training_criteria():
    print("--- Bắt đầu tạo dữ liệu Tiêu chí rèn luyện (Training Criteria) ---")
    created_count = 0
    for data in training_criteria_data:
        obj, created = TrainingCriterion.objects.get_or_create(
            code=data["code"],
            defaults={
                "name": data["name"],
                "max_points": data["max_points"],
            }
        )
        if created:
            created_count += 1
        else:
            if obj.name != data["name"] or obj.max_points != data["max_points"]:
                obj.name = data["name"]
                obj.max_points = data["max_points"]
                obj.save()
    print(f"-> Đã tạo mới/cập nhật {len(training_criteria_data)} Tiêu chí rèn luyện (tạo mới {created_count}).\n")


def seed_events():
    print("--- Bắt đầu tạo dữ liệu Sự kiện (Events) ---")
    tc2 = TrainingCriterion.objects.get(code="TC2")  # Học thuật
    tc3 = TrainingCriterion.objects.get(code="TC3")  # Văn hóa
    tc4 = TrainingCriterion.objects.get(code="TC4")  # Tình nguyện

    cat_hocthuat, _ = EventCategory.objects.get_or_create(name="Học thuật", defaults={"criterion": tc2})
    cat_vanhoa, _ = EventCategory.objects.get_or_create(name="Văn hóa - Văn nghệ", defaults={"criterion": tc3})
    cat_tinhnguyen, _ = EventCategory.objects.get_or_create(name="Tình nguyện", defaults={"criterion": tc4})
    cat_diengiang, _ = EventCategory.objects.get_or_create(name="Diễn giảng", defaults={"criterion": tc2})

    org_doanhoi = User.objects.get(username="doanhoi")
    org_clb = User.objects.get(username="clb")

    now = timezone.now()
    events_data = [
        {
            "title": "Chiến dịch Xuân Tình Nguyện 2025",
            "category": cat_tinhnguyen,
            "organizer": org_doanhoi,
            "start_time": now + timedelta(days=6),
            "end_time": now + timedelta(days=8),
            "max_participants": 20,
            "status": "APPROVED",
            "training_points": 10,
        },
        {
            "title": "Diễn giảng: Hành trang Sinh viên 5 Tốt",
            "category": cat_diengiang,
            "organizer": org_doanhoi,
            "start_time": now + timedelta(days=10),
            "end_time": now + timedelta(days=10) + timedelta(hours=2),
            "max_participants": 2,
            "waiting_list_capacity": 10,
            "status": "APPROVED",
            "training_points": 8,
        },
        {
            "title": "Hội thảo AI & Tương lai",
            "category": cat_hocthuat,
            "organizer": org_clb,
            "start_time": now + timedelta(days=30),
            "end_time": now + timedelta(days=30) + timedelta(hours=3),
            "max_participants": 200,
            "status": "APPROVED",
            "training_points": 5,
        }
    ]

    events_list = []
    for ed in events_data:
        ev, created = Event.objects.get_or_create(
            title=ed["title"],
            defaults={
                "description": "Mô tả chi tiết sự kiện...",
                "category": ed["category"],
                "organizer": ed["organizer"],
                "start_time": ed["start_time"],
                "end_time": ed["end_time"],
                "location": "Hội trường A",
                "max_participants": ed["max_participants"],
                "waiting_list_capacity": ed.get("waiting_list_capacity", 0),
                "status": ed["status"],
                "training_points": ed["training_points"],
            }
        )
        events_list.append(ev)

        if created:
            CheckInSession.objects.create(
                event=ev,
                dynamic_code=f"QR_{ev.id}_{random.randint(1000, 9999)}",
                expires_at=ed["end_time"]
            )

    k25_students = list(StudentProfile.objects.filter(cohort__code="K25"))
    for ev in events_list:
        if ev.title == "Diễn giảng: Hành trang Sinh viên 5 Tốt":
            # Setup riêng kịch bản Hủy đăng ký / Danh sách chờ
            sv_user = User.objects.get(username="sv")
            # 1. Đăng ký 'sv' là 1 trong 2 người có vé chính thức
            EventRegistration.objects.get_or_create(
                event=ev, student=sv_user.student_profile,
                defaults={"status": "REGISTERED", "is_checked_in": False}
            )
            # 2. Đăng ký người thứ 2 (để lấp đầy max_participants=2)
            other_student = [s for s in k25_students if s.id != sv_user.student_profile.id][0]
            EventRegistration.objects.get_or_create(
                event=ev, student=other_student,
                defaults={"status": "REGISTERED", "is_checked_in": False}
            )
            # 3. Thêm 3 người vào danh sách chờ
            waitlist_students = [s for s in k25_students if s.id not in [sv_user.student_profile.id, other_student.id]][:3]
            for i, st in enumerate(waitlist_students):
                EventRegistration.objects.get_or_create(
                    event=ev, student=st,
                    defaults={"status": "WAITLIST", "queue_position": i + 1}
                )
            continue

        participants = random.sample(k25_students, min(20, len(k25_students)))
        for st in participants:
            is_sv = (st.user.username == "sv")
            EventRegistration.objects.get_or_create(
                event=ev,
                student=st,
                defaults={
                    "status": "REGISTERED",
                    "is_checked_in": not is_sv,
                    "check_in_time": None if is_sv else (ev.start_time + timedelta(minutes=10))
                }
            )
    print("-> Đã hoàn tất tạo Sự kiện và Điểm danh.\n")


def seed_training_points():
    print("--- Bắt đầu tạo dữ liệu Bảng điểm Rèn luyện (Training Points) ---")
    k25_students = StudentProfile.objects.filter(cohort__code="K25")
    sem20251 = Semester.objects.get(code="20251")
    criteria = TrainingCriterion.objects.all()

    for st in k25_students:
        ssp, created = StudentSemesterPoint.objects.get_or_create(
            student=st,
            semester=sem20251,
            defaults={
                "status": "FACULTY_APPROVED",
                "class_approved_at": timezone.now() - timedelta(days=10),
                "faculty_approved_at": timezone.now() - timedelta(days=5),
            }
        )

        if created:
            if st.homeroom_class and st.homeroom_class.advisor:
                ssp.class_approved_by = st.homeroom_class.advisor.user

            total_st = 0
            total_cl = 0
            total_fn = 0
            for crit in criteria:
                base = int(crit.max_points * 0.8)

                regs = EventRegistration.objects.filter(
                    student=st,
                    is_checked_in=True,
                    event__category__criterion=crit
                )
                event_pts = sum(r.event.training_points for r in regs)

                student_score = min(crit.max_points, base + event_pts)
                class_score = student_score
                final_score = student_score

                SemesterPointDetail.objects.create(
                    semester_point=ssp,
                    criterion=crit,
                    student_score=student_score,
                    class_score=class_score,
                    final_score=final_score
                )

                total_st += student_score
                total_cl += class_score
                total_fn += final_score

            ssp.total_student_score = total_st
            ssp.total_class_score = total_cl
            ssp.total_final_score = total_fn
            ssp.save()

    print("-> Đã hoàn tất tạo và tính Điểm rèn luyện.\n")


def seed_academics_extra():
    print("--- Bắt đầu tạo dữ liệu Học vụ & Sổ Đoàn mở rộng ---")
    k25_students = StudentProfile.objects.filter(cohort__code="K25")
    sem20251 = Semester.objects.get(code="20251")

    # 1. Bảng điểm tổng kết học kỳ
    for st in k25_students:
        courses = StudentCourse.objects.filter(student=st, course_class__semester=sem20251)
        if courses.exists():
            total_credits = 0
            total_score_10 = Decimal(0)
            total_score_4 = Decimal(0)

            for c in courses:
                creds = c.course_class.subject.credits
                total_credits += creds
                if c.total_score_10 is not None:
                    total_score_10 += c.total_score_10 * creds
                if c.total_score_4 is not None:
                    total_score_4 += c.total_score_4 * creds

            if total_credits > 0:
                gpa_10 = total_score_10 / total_credits
                gpa_4 = total_score_4 / total_credits

                StudentSemesterSummary.objects.get_or_create(
                    student=st,
                    semester=sem20251,
                    defaults={
                        "semester_gpa_4": round(gpa_4, 2),
                        "semester_earned_credits": total_credits,
                        "semester_training_points": 85,
                        "training_point_classification": "Tốt",
                        "cumulative_gpa_4": round(gpa_4, 2),
                        "cumulative_earned_credits": total_credits,
                        "cumulative_training_points": 85
                    }
                )

    # 2. Sổ Đoàn
    for st in k25_students[:10]:
        YouthUnionRecord.objects.get_or_create(
            student=st,
            activity_name="Kết nạp Đoàn Thanh niên Cộng sản Hồ Chí Minh",
            date=date(2022, 3, 26),
            defaults={
                "description": "Kết nạp tại trường THPT",
                "sync_status": "SYNCED"
            }
        )

    # 3. Nhật ký đồng bộ hệ thống (IntegrationSyncLog)
    IntegrationSyncLog.objects.get_or_create(
        sync_type="SCORES",
        defaults={
            "status": "SUCCESS",
            "error_details": {"message": "Đã đồng bộ thành công điểm thi."}
        }
    )
    print("-> Đã tạo xong dữ liệu GPA, Sổ Đoàn và Lịch sử đồng bộ.\n")


def seed_training_points_extra():
    print("--- Bắt đầu tạo dữ liệu Minh chứng & Lịch sử Điểm Rèn luyện ---")
    k25_students = StudentProfile.objects.filter(cohort__code="K25")
    sem20251 = Semester.objects.get(code="20251")
    tc6 = TrainingCriterion.objects.get(code="TC6")

    # 1. Nộp minh chứng (PointProof)
    for st in k25_students[:5]:
        # Cần lấy/tạo SemesterPointDetail trước
        semester_point, _ = StudentSemesterPoint.objects.get_or_create(
            student=st, semester=sem20251
        )
        point_detail, _ = SemesterPointDetail.objects.get_or_create(
            semester_point=semester_point, criterion=tc6
        )
        
        PointProof.objects.get_or_create(
            point_detail=point_detail,
            activity_name="Đạt giải Nhất cuộc thi Sáng tạo sinh viên",
            defaults={
                "status": "APPROVED",
                "file_url": "point_proofs/sample.pdf"
            }
        )

    # 2. Lịch sử điểm (PointHistory)
    for st in k25_students[:10]:
        PointHistory.objects.get_or_create(
            student=st,
            semester=sem20251,
            criterion=tc6,
            points_changed=10,
            reason="Được cộng điểm do nộp giấy khen ngoài trường"
        )
    print("-> Đã tạo xong Minh chứng và Lịch sử điểm.\n")


def seed_finance():
    print("--- Bắt đầu tạo dữ liệu Tài chính & Học phí ---")
    admin = User.objects.get(username="admin")
    sem20251 = Semester.objects.get(code="20251")
    sem_ct = ContentType.objects.get_for_model(Semester)

    # 1. Tạo khoản thu
    tuition_fee, _ = Fee.objects.get_or_create(
        title=f"Học phí học kỳ {sem20251.code}",
        content_type=sem_ct,
        object_id=sem20251.id,
        fee_type="TUITION",
        defaults={
            "description": "Học phí tín chỉ học kỳ 1 năm học 2025-2026",
            "amount": Decimal("15000000.00"),
            "is_mandatory": True,
            "creator": admin,
            "due_date": timezone.now() + timedelta(days=30)
        }
    )

    union_fee, _ = Fee.objects.get_or_create(
        title=f"Đoàn phí học kỳ {sem20251.code}",
        content_type=sem_ct,
        object_id=sem20251.id,
        fee_type="YOUTH_UNION_FEE",
        defaults={
            "description": "Đoàn phí định kỳ",
            "amount": Decimal("50000.00"),
            "is_mandatory": True,
            "creator": admin,
            "due_date": timezone.now() + timedelta(days=30)
        }
    )

    # 2. Tạo thanh toán cho sinh viên K25
    k25_students = list(StudentProfile.objects.filter(cohort__code="K25"))
    for st in k25_students[:15]:
        Payment.objects.get_or_create(
            student=st,
            fee=tuition_fee,
            defaults={
                "amount": tuition_fee.amount,
                "status": "SUCCESS",
                "payment_method": "VNPAY",
                "transaction_id": f"VNP_{random.randint(100000, 999999)}",
                "paid_at": timezone.now() - timedelta(days=5)
            }
        )

    for st in k25_students[15:20]:
        Payment.objects.get_or_create(
            student=st,
            fee=tuition_fee,
            defaults={
                "amount": tuition_fee.amount,
                "status": "PENDING",
                "payment_method": "MOMO",
            }
        )
    print("-> Đã tạo xong Khoản thu và Thanh toán.\n")


def seed_support():
    print("--- Bắt đầu tạo dữ liệu Hỗ trợ sinh viên ---")
    k25_students = StudentProfile.objects.filter(cohort__code="K25")



    admin = User.objects.get(username="admin")
    FacilityReport.objects.get_or_create(
        reporter=admin,
        room="A1-101",
        defaults={
            "description": "Hỏng quạt trần số 2",
            "priority": "MEDIUM",
            "status": "PENDING"
        }
    )

    Complaint.objects.get_or_create(
        reporter=admin,
        title="Wifi thư viện quá chậm",
        defaults={
            "description": "Sinh viên không thể truy cập tài liệu được.",
            "priority": "HIGH",
            "status": "PROCESSING"
        }
    )
    print("-> Đã tạo xong Hỗ trợ sinh viên.\n")


def seed_system():
    print("--- Bắt đầu tạo dữ liệu Hệ thống & Thông báo ---")
    admin = User.objects.get(username="admin")

    SystemConfig.objects.get_or_create(key="ALLOW_REGISTRATION", defaults={"value": "True", "updated_by": admin})
    SystemConfig.objects.get_or_create(key="SYSTEM_VERSION", defaults={"value": "1.0.0", "updated_by": admin})
    SystemConfig.objects.get_or_create(key="SEMESTERS_PER_YEAR", defaults={"value": "3", "description": "Số học kỳ trong một năm học", "updated_by": admin})

    tpl, _ = NotificationTemplate.objects.get_or_create(
        title="Nhắc nhở đóng học phí",
        defaults={
            "sender": admin,
            "message": "Bạn có khoản học phí chưa thanh toán. Vui lòng thanh toán trước hạn.",
            "type": "REMINDER",
            "related_link": "/finance/payments"
        }
    )

    pending_payments = Payment.objects.filter(status="PENDING")
    for payment in pending_payments:
        UserNotification.objects.get_or_create(
            user=payment.student.user,
            template=tpl,
            defaults={"is_read": False}
        )

    # Tạo thiết bị nhận thông báo (UserDevice)
    UserDevice.objects.get_or_create(
        user=admin,
        defaults={
            "fcm_token": "dummy_firebase_token_ios_12345",
            "device_os": "IOS"
        }
    )
    print("-> Đã tạo xong Cấu hình hệ thống, Thông báo và Thiết bị.\n")


def run():
    print("Đang xóa sạch dữ liệu cũ và reset auto-increment...")
    call_command("flush", interactive=False)
    print("Đã xóa xong. Bắt đầu seed data mới...")

    seed_faculties_and_majors()
    seed_cohorts()
    seed_grade_conversion_rules()
    seed_semesters()
    seed_subjects()
    seed_education_programs()
    seed_users()
    seed_classes_and_scores()
    seed_training_criteria()
    seed_events()
    seed_training_points()
    seed_academics_extra()
    seed_training_points_extra()
    seed_finance()
    seed_support()
    seed_system()
    print("==== Hoàn tất toàn bộ việc tạo dữ liệu mẫu (Seed Data) ====")


if __name__ == "__main__":
    run()
