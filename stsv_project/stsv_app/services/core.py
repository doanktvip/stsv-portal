from .base import BaseService
from stsv_app.models.core import Faculty, Major, Cohort
from .exceptions import ResourceNotFoundError, ValidationError

class FacultyService(BaseService):
    def get_all_faculties(self):
        return Faculty.objects.all()

    def get_faculty_by_id(self, faculty_id: int) -> Faculty:
        try:
            return Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            raise ResourceNotFoundError(f"Không tìm thấy khoa với ID {faculty_id}")

class MajorService(BaseService):
    def get_majors_by_faculty(self, faculty_id: int):
        return Major.objects.filter(faculty_id=faculty_id)

class CohortService(BaseService):
    def get_all_cohorts(self):
        return Cohort.objects.all()
