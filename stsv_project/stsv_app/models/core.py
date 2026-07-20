from django.db import models


class Faculty(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Major(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="majors"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Cohort(models.Model):
    code = models.CharField(max_length=20, unique=True)
    enrollment_year = models.IntegerField()

    def __str__(self):
        return self.code
