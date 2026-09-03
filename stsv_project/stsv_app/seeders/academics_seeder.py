from django.utils import timezone
from datetime import timedelta
import random
from stsv_app.models.core import Faculty, Major, Cohort
from stsv_app.models.academics import GradeConversionRule, Semester, Subject, CourseClass, Schedule, StudentCourse, StudentScoreDetail, ScoreComponent, StudentSemesterSummary
from stsv_app.models.users import User, StudentProfile, LecturerProfile
from stsv_app.seeders.data import grade_conversion_rules_data, subjects_data, semesters_data

def seed_academics(num_students=50):
    print("--- Seeding Academics Data ---")
    now = timezone.now()

    for rule_data in grade_conversion_rules_data:
        GradeConversionRule.objects.get_or_create(
            letter_grade=rule_data["letter"],
            defaults={
                "min_score_10": rule_data["min"],
                "max_score_10": rule_data["max"],
                "score_4": rule_data["score4"],
                "classification": rule_data["classification"],
            },
        )

    for sem_data in semesters_data:
        Semester.objects.get_or_create(
            code=sem_data["code"],
            defaults={
                "start_date": sem_data["start_date"],
                "end_date": sem_data["end_date"]
            }
        )

    # Re-fetch faculties map
    faculties_map = {f.code: f for f in Faculty.objects.all()}

    # Subjects
    subjects_to_create = []
    existing_subjects = set(Subject.objects.values_list('subject_code', flat=True))
    for s_data in subjects_data:
        if s_data["code"] not in existing_subjects:
            f = faculties_map.get(s_data["faculty_code"])
            if f:
                subjects_to_create.append(Subject(
                    subject_code=s_data["code"],
                    name=s_data["name"],
                    credits=s_data["credits"],
                    faculty=f
                ))
    if subjects_to_create:
        Subject.objects.bulk_create(subjects_to_create)

    # ScoreComponents
    subjects = list(Subject.objects.all())
    components_to_create = []
    existing_comps = set(ScoreComponent.objects.values_list('subject_id', 'name'))
    for subject in subjects:
        for comp_name, weight in [("Chuyên cần", 10), ("Giữa kỳ", 30), ("Cuối kỳ", 60)]:
            if (subject.id, comp_name) not in existing_comps:
                components_to_create.append(ScoreComponent(
                    subject=subject,
                    name=comp_name,
                    weight_percentage=weight
                ))
    if components_to_create:
        ScoreComponent.objects.bulk_create(components_to_create)
    
    # Load Lecturers
    lecturers = list(LecturerProfile.objects.all())
    if not lecturers:
        print("Missing lecturers. Skipping classes.")
        return
        
    semesters = list(Semester.objects.all())
    if not semesters:
        return

    # Course classes and schedules
    print("Seeding Course Classes and Schedules...")
    classes_to_create = []
    for _ in range(30):  # Create 30 random classes
        subject = random.choice(subjects)
        semester = random.choice(semesters)
        lecturer = random.choice(lecturers)
        
        class_code = f"{subject.subject_code}.{semester.code}.{random.randint(1,9):02d}"
        if not CourseClass.objects.filter(class_code=class_code).exists():
            classes_to_create.append(CourseClass(
                class_code=class_code,
                subject=subject,
                semester=semester,
                lecturer=lecturer,
                capacity=random.randint(40, 100),
                current_enrollment=0
            ))
            
    if classes_to_create:
        CourseClass.objects.bulk_create(classes_to_create)

    created_classes = list(CourseClass.objects.all())
    
    schedules_to_create = []
    rooms = ["A1-101", "B1-205", "C1-301", "D1-402"]
    
    for c_class in created_classes:
        if not Schedule.objects.filter(course_class=c_class).exists():
            start_date = c_class.semester.start_date
            # Create a regular class schedule
            schedules_to_create.append(Schedule(
                course_class=c_class,
                type=Schedule.Type.CLASS,
                day_of_week=random.randint(2, 7),
                exact_date=start_date + timedelta(days=random.randint(1, 14)),
                start_time=timezone.datetime.strptime("07:00", "%H:%M").time(),
                end_time=timezone.datetime.strptime("09:30", "%H:%M").time(),
                room=random.choice(rooms)
            ))
    if schedules_to_create:
        Schedule.objects.bulk_create(schedules_to_create)

    # Student Enrollments and Scores
    print("Seeding Enrollments and Scores...")
    students = list(StudentProfile.objects.all()[:num_students])
    if not students or not created_classes:
        return
        
    enrollments_to_create = []
    
    for student in students:
        # Enroll in 3-5 random classes
        for c_class in random.sample(created_classes, k=random.randint(3, 5)):
            if not StudentCourse.objects.filter(student=student, course_class=c_class).exists():
                enrollments_to_create.append(StudentCourse(
                    student=student,
                    course_class=c_class,
                    is_passed=random.choice([True, False, None])
                ))
    if enrollments_to_create:
        StudentCourse.objects.bulk_create(enrollments_to_create)

    enrollments = StudentCourse.objects.filter(student__in=students)
    comps_map = {}
    for c in ScoreComponent.objects.all():
        if c.subject_id not in comps_map:
            comps_map[c.subject_id] = []
        comps_map[c.subject_id].append(c)

    scores_to_create = []
    for enr in enrollments:
        if not StudentScoreDetail.objects.filter(student_course=enr).exists():
            comps = comps_map.get(enr.course_class.subject_id, [])
            for comp in comps:
                scores_to_create.append(StudentScoreDetail(
                    student_course=enr,
                    score_component=comp,
                    score_value=random.uniform(5.0, 10.0)
                ))
    if scores_to_create:
        StudentScoreDetail.objects.bulk_create(scores_to_create)

    # Seed Student Semester Summaries
    print("Seeding Student Semester Summaries...")
    summaries_to_create = []
    
    # Get all distinct (student, semester) pairs from enrollments
    student_semesters = set()
    for enr in enrollments:
        student_semesters.add((enr.student_id, enr.course_class.semester_id))
        
    for student_id, semester_id in student_semesters:
        if not StudentSemesterSummary.objects.filter(student_id=student_id, semester_id=semester_id).exists():
            summaries_to_create.append(StudentSemesterSummary(
                student_id=student_id,
                semester_id=semester_id,
                semester_gpa_4=random.uniform(2.0, 4.0),
                semester_earned_credits=random.randint(10, 20),
                semester_training_points=random.randint(70, 100),
                training_point_classification=random.choice(["Xuất sắc", "Tốt", "Khá"]),
                cumulative_gpa_4=random.uniform(2.5, 4.0),
                cumulative_earned_credits=random.randint(20, 100),
                cumulative_training_points=random.randint(70, 100)
            ))
            
    if summaries_to_create:
        StudentSemesterSummary.objects.bulk_create(summaries_to_create)

    print("Academics data seeded successfully.")
