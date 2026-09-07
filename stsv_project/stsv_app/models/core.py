from django.db import models


# Khoa (Ví dụ: Khoa CNTT, Khoa Kinh tế). Quản lý thông tin các khoa trong trường.
class Faculty(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"



# Lớp sinh hoạt (Lớp hành chính, VD: K25-CNTT-01). 
class HomeroomClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="homeroom_classes", null=True)
    cohort_year = models.IntegerField(default=2023, help_text="Năm nhập học (VD: 2023)")
    president = models.ForeignKey(
        "stsv_app.StudentProfile", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="presided_classes"
    )

    def __str__(self):
        return self.name
