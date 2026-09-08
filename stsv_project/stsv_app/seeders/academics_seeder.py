from stsv_app.models import Semester
from .data import semesters_data

def seed_academics(num_students=50):
    print("--- Nạp Dữ Liệu Học Tập (Academics) ---")
    for sem_data in semesters_data:
        Semester.objects.get_or_create(
            code=sem_data["code"],
            defaults={
                "start_date": sem_data["start_date"],
                "end_date": sem_data["end_date"]
            }
        )
    print("Nạp dữ liệu học tập thành công.")

