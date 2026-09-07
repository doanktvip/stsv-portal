from django.utils import timezone
from .base import BaseService
from stsv_app.models import User, Semester

class SemesterService(BaseService):
    def get_semesters_for_user(self, user):
        today = timezone.now().date()
        future_date = today + timezone.timedelta(days=60)
        qs = Semester.objects.filter(start_date__lte=future_date)
        
        if user.role == User.Role.STUDENT and hasattr(user, 'student_profile') and user.student_profile.cohort_year:
            enrollment_year = user.student_profile.cohort_year
            qs = qs.filter(start_date__year__gte=enrollment_year)
            
        return qs.order_by("-start_date")
