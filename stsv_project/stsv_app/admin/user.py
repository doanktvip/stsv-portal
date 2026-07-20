from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from stsv_app.models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Khai báo các cột hiển thị bên ngoài danh sách
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "class_name",
        "is_staff",
    )

    # Thêm bộ lọc bên phải
    list_filter = ("role", "faculty", "is_staff", "is_active")

    # Cho phép tìm kiếm bằng MSSV (username), tên, email
    search_fields = ("username", "first_name", "last_name", "email")

    # Phân nhóm các trường hiển thị khi bấm vào sửa 1 user
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin Cá nhân", {"fields": ("first_name", "last_name", "email")}),
        ("Thông tin Sinh viên", {"fields": ("role", "faculty", "class_name", "phone")}),
        (
            "Quyền hạn",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Ngày tháng", {"fields": ("last_login", "date_joined")}),
    )

    # Phân nhóm lúc tạo mới user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password",
                    "role",
                    "faculty",
                    "class_name",
                    "phone",
                ),
            },
        ),
    )
