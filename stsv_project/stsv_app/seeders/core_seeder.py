from stsv_app.models import Faculty, HomeroomClass
from .data import faculties_data

def seed_core():
    print("--- Nạp Dữ Liệu Cốt Lõi (Core Data) ---")
    # Faculities
    for f_data in faculties_data:
        faculty, _ = Faculty.objects.get_or_create(code=f_data["code"], defaults={"name": f_data["name"]})

    # HomeroomClasses
    print("Đang nạp danh sách Lớp sinh hoạt...")
    faculties = Faculty.objects.all()
    classes_to_create = []

    for faculty in faculties:
        for year in [2022, 2023, 2024]:
            for i in range(1, 4):
                class_name = f"{year}-{faculty.code}-{i:02d}"
                if not HomeroomClass.objects.filter(name=class_name).exists():
                    classes_to_create.append(HomeroomClass(
                        name=class_name,
                        faculty=faculty,
                        cohort_year=year
                    ))
    
    if classes_to_create:
        HomeroomClass.objects.bulk_create(classes_to_create)

    print("Nạp dữ liệu cốt lõi thành công.")

