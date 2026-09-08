from .base import BaseService
from .exceptions import ValidationError
from stsv_app.models import StudentSemesterPoint, PointTransaction, TrainingCriterion, Semester, HomeroomClass, TrainingRule
from django.utils import timezone
from django.db.models import Prefetch

class TrainingPointService(BaseService):
    def get_active_semester(self, semester_id=None):
        if semester_id:
            semester = Semester.objects.filter(id=semester_id).first()
            if semester:
                return semester
                
        now = timezone.now().date()
        semester = Semester.objects.filter(start_date__lte=now, end_date__gte=now).first()
        if not semester:
            semester = Semester.objects.first()
            
        return semester
        
    def calculate_student_points(self, semester, student_profile=None):
        if student_profile is None:
            if not hasattr(self.user, 'student_profile'):
                raise ValidationError("Người dùng không phải là sinh viên.")
            student_profile = self.user.student_profile
        

        # Lấy tất cả giao dịch điểm của sinh viên trong 1 query duy nhất
        all_transactions = list(PointTransaction.objects.filter(
            student=student_profile,
            semester=semester
        ).select_related('event__category'))

        approved_transactions = [
            t for t in all_transactions 
            if t.status in [PointTransaction.Status.AUTO_APPROVED, PointTransaction.Status.APPROVED]
        ]
        
        # Tập hợp các rule_id sinh viên đã nộp minh chứng (không bị từ chối)
        rules_with_proof = {
            t.rule_id for t in all_transactions 
            if t.rule_id is not None and t.status != PointTransaction.Status.REJECTED
        }

        # Lấy tất cả Criteria từ Database kèm rules và group tối ưu trong 2 queries
        all_criteria = TrainingCriterion.objects.all().prefetch_related(
            Prefetch('rules', queryset=TrainingRule.objects.select_related('group'))
        )
        
        points_data = {"categories": []}
        total_student_score = 0
        
        for criterion in all_criteria:
            category_score = 0
            groups_dict = {}
            
            # Pre-group rules
            for rule in criterion.rules.all():
                if rule.group:
                    group_id = rule.group.id
                    group_name = rule.group.name
                    is_single_choice = rule.group.is_single_choice
                else:
                    group_id = 0  # pragma: no cover
                    group_name = "Khác"  # pragma: no cover
                    is_single_choice = False  # pragma: no cover
                    
                if group_id not in groups_dict:
                    groups_dict[group_id] = {
                        "id": group_id,
                        "name": group_name,
                        "is_single_choice": is_single_choice,
                        "score": 0,
                        "rules": []
                    }
                
                # Tính tổng điểm cho rule này từ transactions
                rule_score = sum(t.points_changed for t in approved_transactions if t.rule_id == rule.id)
                
                if rule.is_event_rule:
                    event_score = sum(
                        t.points_changed for t in approved_transactions 
                        if t.rule_id is None and t.event and t.event.category and t.event.category.criterion_id == criterion.id
                    )
                    rule_score += event_score
                    
                category_score += rule_score
                groups_dict[group_id]["score"] += rule_score
                
                # Kiểm tra minh chứng (O(1) in-memory lookup)
                has_proof = True if rule.is_event_rule else (rule.id in rules_with_proof)

                if is_single_choice and rule_score > 0:
                    groups_dict[group_id]["selected_rule_id"] = rule.id
                
                groups_dict[group_id]["rules"].append({
                    "id": rule.id,
                    "code": rule.code,
                    "description": rule.description,
                    "max_score": rule.points,
                    "is_proof_required": rule.is_proof_required,
                    "is_event_rule": rule.is_event_rule,
                    "student_score": rule_score,
                    "class_score": rule_score,
                    "faculty_score": rule_score,
                    "has_proof": has_proof
                })
                
            capped_score = min(category_score, criterion.max_points)
            if capped_score < 0:
                capped_score = 0  # pragma: no cover
                
            points_data["categories"].append({
                "code": criterion.name,
                "score": category_score,
                "capped_score": capped_score,
                "max_score": criterion.max_points,
                "groups": list(groups_dict.values())
            })
            total_student_score += capped_score

        if total_student_score > 100:
            total_student_score = 100  # pragma: no cover

        # Lấy hoặc tạo bản ghi StudentSemesterPoint
        semester_point, created = StudentSemesterPoint.objects.get_or_create(
            student=student_profile,
            semester=semester,
            defaults={
                "status": StudentSemesterPoint.Status.DRAFT,
                "total_student_score": total_student_score,
                "points_data": points_data,
            }
        )
        
        if not created:
            semester_point.total_student_score = total_student_score
            semester_point.points_data = points_data
            semester_point.save(update_fields=['total_student_score', 'points_data'])

        return semester_point

    def submit_student_points(self, semester, points_data=None, total_student_score=None, is_draft=False):
        if not semester.is_evaluation_open:
            raise ValidationError("Đợt chấm điểm rèn luyện hiện đang đóng.")
            
        if not hasattr(self.user, 'student_profile'):
            raise ValidationError("Người dùng không phải là sinh viên.")
            
        point = StudentSemesterPoint.objects.filter(student=self.user.student_profile, semester=semester).first()
        if not point:
            raise ValidationError("Chưa có dữ liệu điểm cho học kỳ này.")
            
        if point.status != StudentSemesterPoint.Status.DRAFT:
            raise ValidationError("Bạn đã chốt điểm rồi, không thể sửa lại.")
            
        if points_data is not None:
            point.points_data = points_data
        if total_student_score is None and points_data is not None:
            # Tự động tính lại tổng điểm
            total = sum(cat.get("capped_score", 0) for cat in points_data.get("categories", []))
            point.total_student_score = min(total, 100)
        elif total_student_score is not None:
            point.total_student_score = total_student_score

        if not is_draft:
            point.status = StudentSemesterPoint.Status.SUBMITTED
            
        point.save(update_fields=['status', 'points_data', 'total_student_score'])
        return point

    def open_evaluation(self, semester):
        if not hasattr(self.user, 'org_profile') or self.user.org_profile.org_type != 'FACULTY':
            raise ValidationError("Chỉ cán bộ Khoa mới có quyền mở đợt chấm điểm.")
        semester.is_evaluation_open = True
        semester.save(update_fields=['is_evaluation_open'])

    def get_class_points_list(self, semester):
        presided_classes = self.user.student_profile.presided_classes.all()
        if not presided_classes.exists():
            raise ValidationError("Bạn không phải là lớp trưởng của lớp nào.")
            
        homeroom_class = presided_classes.first()
        students = list(homeroom_class.students.select_related('user', 'homeroom_class'))
        
        existing_points = {
            p.student_id: p
            for p in StudentSemesterPoint.objects.filter(student__in=students, semester=semester).select_related('student__user', 'student__homeroom_class')
        }
        
        points = []
        for student in students:
            point = existing_points.get(student.id)
            if not point or point.status == StudentSemesterPoint.Status.DRAFT:
                point = self.calculate_student_points(semester, student_profile=student)
            points.append(point)
        return homeroom_class.name, points

    def approve_student_points_by_class(self, point, total_class_score=None, class_points_data=None, is_draft=False):
        presided_classes = self.user.student_profile.presided_classes.all()
        if point.student.homeroom_class not in presided_classes:
            raise ValidationError("Bạn không có quyền duyệt điểm cho sinh viên này.")
            
        if point.status not in [StudentSemesterPoint.Status.DRAFT, StudentSemesterPoint.Status.SUBMITTED, StudentSemesterPoint.Status.CLASS_APPROVED]:
            raise ValidationError(f"Không thể duyệt điểm ở trạng thái: {point.status}")
            
        if total_class_score is None:
            total_class_score = point.total_student_score
            
        point.total_class_score = total_class_score
        if class_points_data is not None:
            point.class_points_data = class_points_data
            
        if not is_draft:
            point.status = StudentSemesterPoint.Status.CLASS_APPROVED
            point.class_approved_by = self.user
            point.class_approved_at = timezone.now()
            
        point.save(update_fields=['total_class_score', 'class_points_data', 'status', 'class_approved_by', 'class_approved_at'])
        return point

    def get_faculty_points_list(self, semester, class_id=None):
        if not hasattr(self.user, 'org_profile') or self.user.org_profile.org_type != 'FACULTY':
            raise ValidationError("Bạn không phải là cán bộ Khoa.")
            
        faculty = self.user.org_profile.faculty
        if not faculty:
            raise ValidationError("Tài khoản của bạn chưa được gắn với Khoa nào.")
            
        if class_id:
            target_class = HomeroomClass.objects.filter(id=class_id, faculty=faculty).first()
            if not target_class:
                raise ValidationError("Không tìm thấy lớp này trong Khoa của bạn.")
            
            students = list(target_class.students.select_related('user', 'homeroom_class'))
            existing_points = {
                p.student_id: p
                for p in StudentSemesterPoint.objects.filter(student__in=students, semester=semester).select_related('student__user', 'student__homeroom_class')
            }
            
            points = []
            for student in students:
                point = existing_points.get(student.id)
                if not point or point.status == StudentSemesterPoint.Status.DRAFT:
                    point = self.calculate_student_points(semester, student_profile=student)
                points.append(point)
            
            return points, True
        else:
            classes = faculty.homeroom_classes.all()
            data = []
            for cls in classes:
                total_students = cls.students.count()
                approved_by_class = StudentSemesterPoint.objects.filter(
                    student__homeroom_class=cls, 
                    semester=semester,
                    status__in=[StudentSemesterPoint.Status.CLASS_APPROVED, StudentSemesterPoint.Status.FACULTY_APPROVED]
                ).count()
                data.append({
                    "id": cls.id,
                    "name": cls.name,
                    "total_students": total_students,
                    "approved_by_class": approved_by_class
                })
            return data, False

    def approve_student_points_by_faculty(self, point, total_final_score=None, faculty_points_data=None, is_draft=False):
        if not hasattr(self.user, 'org_profile') or self.user.org_profile.org_type != 'FACULTY':
            raise ValidationError("Bạn không phải là cán bộ Khoa.")
            
        faculty = self.user.org_profile.faculty
        if point.student.faculty != faculty:
            raise ValidationError("Sinh viên này không thuộc Khoa của bạn.")
            
        if point.status not in [StudentSemesterPoint.Status.CLASS_APPROVED, StudentSemesterPoint.Status.FACULTY_APPROVED]:
            raise ValidationError(f"Chưa thể duyệt điểm đang ở trạng thái: {point.status}. Yêu cầu Lớp trưởng duyệt trước.")
            
        if total_final_score is None:
            total_final_score = point.total_class_score
            
        point.total_final_score = total_final_score
        if faculty_points_data is not None:
            point.faculty_points_data = faculty_points_data
            
        if not is_draft:
            point.status = StudentSemesterPoint.Status.FACULTY_APPROVED
            point.faculty_approved_by = self.user.org_profile
            point.faculty_approved_at = timezone.now()
            
        point.save(update_fields=['total_final_score', 'faculty_points_data', 'status', 'faculty_approved_by', 'faculty_approved_at'])
        return point