from django.db import models

# Các model Học thuật (Điểm số, Môn học, Lịch học) đã bị loại bỏ để tối ưu hệ thống.
class Semester(models.Model):
    code = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    is_evaluation_open = models.BooleanField(default=False, help_text="Mở đợt chấm điểm rèn luyện cho toàn trường")
    

    def __str__(self):
        return self.code
