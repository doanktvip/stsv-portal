from django.db import models
from django.contrib.auth.models import AbstractUser
from .core import Faculty, Major, Cohort, HomeroomClass


# Tài khoản đăng nhập hệ thống, chứa username, password, email, role.
class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Sinh viên"
        ADMIN = "ADMIN", "Quản trị viên"
        ORGOFFICER = "ORGOFFICER", "Cán bộ Tổ chức"
        LECTURER = "LECTURER", "Giảng viên"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)


# Quản lý thiết bị của người dùng (dùng để gửi Push Notification tới điện thoại/trình duyệt).
class UserDevice(models.Model):
    class OS(models.TextChoices):
        IOS = "IOS", "iOS"
        ANDROID = "ANDROID", "Android"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    fcm_token = models.CharField(max_length=500, blank=True, null=True)
    device_os = models.CharField(
        max_length=10, choices=OS.choices, blank=True, null=True
    )
    calendar_sync_token = models.CharField(max_length=500, blank=True, null=True)


# Hồ sơ chi tiết của Sinh viên (mã SV, ngày sinh, lớp quản lý,...), liên kết 1-1 với User
class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    major = models.ForeignKey(
        Major, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    cohort = models.ForeignKey(
        Cohort, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    homeroom_class = models.ForeignKey(
        HomeroomClass, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    is_youth_union_linked = models.BooleanField(default=False)
    youth_union_token = models.CharField(max_length=500, blank=True, null=True)
    last_sync_youth_union = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"


# Hồ sơ chi tiết của Giảng viên.
class LecturerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="lecturer_profile"
    )
    lecturer_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, related_name="lecturers"
    )
    department = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name


# Hồ sơ của các Tổ chức/Câu lạc bộ/Phòng ban trong trường.
class OrgProfile(models.Model):
    class OrgType(models.TextChoices):
        FACULTY = "FACULTY", "Cấp Khoa"
        YOUTH_UNION_ASSOC = "YOUTH_UNION_ASSOC", "Đoàn - Hội"
        CLUB = "CLUB", "Câu lạc bộ"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Hoạt động"
        SUSPENDED = "SUSPENDED", "Đình chỉ"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="org_profile"
    )
    org_name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=OrgType.choices)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, blank=True
    )
    parent_org = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField(blank=True)
    established_date = models.DateField(null=True, blank=True)
    advisor = models.ForeignKey(
        LecturerProfile, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.org_name
