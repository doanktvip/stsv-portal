from django.utils import timezone
from datetime import timedelta
import random
from stsv_app.models.training_points import TrainingCriterion, StudentSemesterPoint, SemesterPointDetail, PointProof
from stsv_app.models.users import StudentProfile
from stsv_app.models.academics import Semester


def seed_training_points():
    print("--- Seeding Training Points Data ---")
    
    # Pre-create criteria
    criterions = []
    criterion_group, _ = TrainingCriterion.objects.get_or_create(code="TC1", defaults={"name": "Ý thức tham gia học tập", "max_points": 20})
    criterion_child1, _ = TrainingCriterion.objects.get_or_create(code="TC1.1", defaults={"name": "Đi học đầy đủ", "max_points": 10, "parent": criterion_group})
    criterion_child2, _ = TrainingCriterion.objects.get_or_create(code="TC1.2", defaults={"name": "Kết quả học tập xuất sắc", "max_points": 10, "parent": criterion_group})
    
    criterions.extend([criterion_child1, criterion_child2])

    students = list(StudentProfile.objects.all())
    semesters = list(Semester.objects.all())
    if not students or not semesters:
        return

    # Filter out empty students
    students = [s for s in students if s.user.is_active]

    semester_points_to_create = []
    
    # For every active student in a random semester
    print("Seeding Semester Points...")
    student_semesters = []
    for student in students:
        # Generate for 1-2 semesters
        for semester in random.sample(semesters, k=random.randint(1, min(2, len(semesters)))):
            student_semesters.append((student, semester))
            
    for student, semester in student_semesters:
        if not StudentSemesterPoint.objects.filter(student=student, semester=semester).exists():
            score = random.randint(50, 100)
            semester_points_to_create.append(StudentSemesterPoint(
                student=student, 
                semester=semester, 
                total_student_score=score, 
                total_class_score=score, 
                total_final_score=score
            ))

    if semester_points_to_create:
        StudentSemesterPoint.objects.bulk_create(semester_points_to_create)

    # Fetch created points
    created_points = list(StudentSemesterPoint.objects.all())
    
    point_details_to_create = []
    for s_point in created_points:
        for crit in criterions:
            if not SemesterPointDetail.objects.filter(semester_point=s_point, criterion=crit).exists():
                point_details_to_create.append(SemesterPointDetail(
                    semester_point=s_point,
                    criterion=crit,
                    student_score=random.randint(0, crit.max_points),
                    class_score=random.randint(0, crit.max_points),
                    final_score=random.randint(0, crit.max_points)
                ))
    if point_details_to_create:
        SemesterPointDetail.objects.bulk_create(point_details_to_create)

    created_details = list(SemesterPointDetail.objects.all())
    point_proofs_to_create = []
    
    print("Seeding Point Proofs...")
    for detail in random.sample(created_details, k=min(50, len(created_details))):
        for status in PointProof.Status.choices:
            if random.random() < 0.3:
                point_proofs_to_create.append(PointProof(
                    point_detail=detail,
                    activity_name=f"Minh chứng {random.randint(1000, 9999)}",
                    file_url="https://dummyimage.com/400x400/000/fff.jpg&text=Proof",
                    status=status[0]
                ))
    if point_proofs_to_create:
        PointProof.objects.bulk_create(point_proofs_to_create)

    print("Training points data seeded successfully.")
