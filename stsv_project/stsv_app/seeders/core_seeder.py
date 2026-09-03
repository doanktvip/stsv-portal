from stsv_app.models.core import Faculty, Major, Cohort, HomeroomClass
from stsv_app.seeders.data import faculties_data, cohorts_data

def seed_core():
    print("--- Seeding Core Data ---")
    # Faculities
    for f_data in faculties_data:
        faculty, _ = Faculty.objects.get_or_create(code=f_data["code"], defaults={"name": f_data["name"]})
        for m_data in f_data["majors"]:
            Major.objects.get_or_create(code=m_data["code"], defaults={"name": m_data["name"], "faculty": faculty})

    # Cohorts
    for c_data in cohorts_data:
        Cohort.objects.get_or_create(code=c_data["code"], defaults={"enrollment_year": c_data["enrollment_year"]})

    # HomeroomClasses
    print("Seeding Homeroom Classes...")
    cohorts = Cohort.objects.all()
    majors = Major.objects.all()
    classes_to_create = []

    for cohort in cohorts:
        for major in majors:
            for i in range(1, 4):  # 3 classes per major per cohort
                class_name = f"{cohort.code}-{major.code}-{i:02d}"
                if not HomeroomClass.objects.filter(name=class_name).exists():
                    classes_to_create.append(HomeroomClass(
                        name=class_name,
                        major=major,
                        cohort=cohort
                    ))
    
    if classes_to_create:
        HomeroomClass.objects.bulk_create(classes_to_create)

    print("Core data seeded successfully.")
