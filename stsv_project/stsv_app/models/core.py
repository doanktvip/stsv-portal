from django.db import models


# Khoa (Ví dụ: Khoa CNTT, Khoa Kinh tế). Quản lý thông tin các khoa trong trường.
class Faculty(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"


# Chuyên ngành đào tạo (Ví dụ: Kỹ thuật phần mềm, Quản trị kinh doanh). Thuộc về một Khoa.
class Major(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="majors"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


# Khóa học (Ví dụ: K64, K65). Dùng để phân loại sinh viên theo năm nhập học.
class Cohort(models.Model):
    code = models.CharField(max_length=20, unique=True)
    enrollment_year = models.IntegerField()

    def __str__(self):
        return self.code


# Lớp sinh hoạt (Lớp hành chính, VD: K25-CNTT-01). 
class HomeroomClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="homeroom_classes")
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name="homeroom_classes")
    advisor = models.ForeignKey(
        "stsv_app.LecturerProfile", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="advised_classes"
    )
    president = models.ForeignKey(
        "stsv_app.StudentProfile", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="presided_classes"
    )

    def __str__(self):
        return self.name
