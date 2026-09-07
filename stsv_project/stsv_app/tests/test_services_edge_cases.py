from django.utils import timezone
from .base import BaseAPITestCase
from stsv_app.models import (
    StudentSemesterPoint, Semester, HomeroomClass, StudentProfile, OrgProfile,
    TrainingCriterion, TrainingRule, PointTransaction, TrainingRuleGroup, Event, EventCategory,
    FeeCampaign, User
)
from stsv_app.services import TrainingPointService, FinanceService
from stsv_app.services.exceptions import ValidationError

class ServicesEdgeCasesTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.semester = Semester.objects.first()
        if not self.semester: # pragma: no cover
            self.semester = Semester.objects.create(
                name="HK1 2024",
                start_date=timezone.now().date(),
                end_date=timezone.now().date(),
                is_evaluation_open=True
            )
        self.tp_service = TrainingPointService()
        self.finance_service = FinanceService()

    def test_get_active_semester_without_id(self):
        # Line 14-19
        sem = self.tp_service.get_active_semester()
        self.assertIsNotNone(sem)
        
    def test_calculate_student_points_no_profile(self):
        # Line 24: "Người dùng không phải là sinh viên."
        self.tp_service.user = self.org_officer
        with self.assertRaises(ValidationError) as cm:
            self.tp_service.calculate_student_points(self.semester)
        self.assertEqual(cm.exception.message, "Người dùng không phải là sinh viên.")
        
    def test_calculate_student_points_with_event_and_group(self):
        # Lines 59-96, 111, 123
        self.tp_service.user = self.student
        student_prof = self.student.student_profile
        
        # Create criteria, group, rule, event, transaction
        crit = TrainingCriterion.objects.create(name="Crit 1", max_points=20)
        group = TrainingRuleGroup.objects.create(criterion=crit, name="Group 1", is_single_choice=True)
        rule = TrainingRule.objects.create(criterion=crit, group=group, code="R1", description="R1", points=10, is_event_rule=True)
        rule2 = TrainingRule.objects.create(criterion=crit, group=group, code="R2", description="R2", points=15, is_event_rule=False)
        cat = EventCategory.objects.create(name="Cat 1", criterion=crit)
        event = Event.objects.create(title="Event 1", category=cat, point_reward=10, organizer=self.org_officer.org_profile, start_time=timezone.now(), end_time=timezone.now() + timezone.timedelta(hours=1))
        
        # Add transactions
        PointTransaction.objects.create(
            student=student_prof, semester=self.semester, event=event, points_changed=10, status=PointTransaction.Status.APPROVED
        )
        PointTransaction.objects.create(
            student=student_prof, semester=self.semester, rule=rule2, points_changed=15, status=PointTransaction.Status.APPROVED
        )
        
        # Calculate
        res = self.tp_service.calculate_student_points(self.semester, student_profile=student_prof)
        self.assertIsNotNone(res)
        
    def test_submit_student_points_no_student(self):
        # Line 148
        self.tp_service.user = self.org_officer
        self.semester.is_evaluation_open = True
        self.semester.save()
        with self.assertRaises(ValidationError) as cm:
            self.tp_service.submit_student_points(self.semester)
            
    def test_submit_student_points_no_data(self):
        # Line 152
        self.tp_service.user = self.student
        self.semester.is_evaluation_open = True
        self.semester.save()
        StudentSemesterPoint.objects.filter(student=self.student.student_profile, semester=self.semester).delete()
        with self.assertRaises(ValidationError):
            self.tp_service.submit_student_points(self.semester)
            
    def test_submit_student_points_already_submitted(self):
        # Line 155
        self.tp_service.user = self.student
        self.semester.is_evaluation_open = True
        self.semester.save()
        point, _ = StudentSemesterPoint.objects.get_or_create(
            student=self.student.student_profile, semester=self.semester, defaults={'status': StudentSemesterPoint.Status.SUBMITTED}
        )
        point.status = StudentSemesterPoint.Status.SUBMITTED
        point.save()
        with self.assertRaises(ValidationError):
            self.tp_service.submit_student_points(self.semester)

    def test_submit_student_points_total_none(self):
        # Line 161-162
        self.tp_service.user = self.student
        self.semester.is_evaluation_open = True
        self.semester.save()
        point, _ = StudentSemesterPoint.objects.get_or_create(
            student=self.student.student_profile, semester=self.semester, defaults={'status': StudentSemesterPoint.Status.DRAFT}
        )
        point.status = StudentSemesterPoint.Status.DRAFT
        point.save()
        points_data = {"categories": [{"capped_score": 15}, {"capped_score": 20}]}
        res = self.tp_service.submit_student_points(self.semester, points_data=points_data, total_student_score=None)
        self.assertEqual(res.total_student_score, 35)

    def test_open_evaluation_not_faculty(self):
        # Line 174
        self.tp_service.user = self.student
        with self.assertRaises(ValidationError):
            self.tp_service.open_evaluation(self.semester)

    def test_get_class_points_list_not_president(self):
        # Line 181
        self.tp_service.user = self.student
        # Ensure not president
        HomeroomClass.objects.filter(president=self.student.student_profile).update(president=None)
        with self.assertRaises(ValidationError):
            self.tp_service.get_class_points_list(self.semester)

    def test_approve_student_points_by_class_not_in_class(self):
        # Line 202
        self.tp_service.user = self.bancansu
        other_class = HomeroomClass.objects.create(name="Other Class")
        other_student_user = User.objects.create_user(username="otherstudent", password="123")
        other_student = StudentProfile.objects.create(user=other_student_user, homeroom_class=other_class, student_id="123999")
        point = StudentSemesterPoint.objects.create(student=other_student, semester=self.semester, status=StudentSemesterPoint.Status.SUBMITTED)
        with self.assertRaises(ValidationError):
            self.tp_service.approve_student_points_by_class(point)
            
    def test_approve_student_points_by_class_wrong_status(self):
        # Line 205
        self.tp_service.user = self.bancansu
        hc = self.student.student_profile.homeroom_class
        hc.president = self.bancansu.student_profile
        hc.save()
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.FACULTY_APPROVED)
        with self.assertRaises(ValidationError):
            self.tp_service.approve_student_points_by_class(point)

    def test_approve_student_points_by_class_total_none(self):
        # Line 208
        self.tp_service.user = self.bancansu
        hc = self.student.student_profile.homeroom_class
        hc.president = self.bancansu.student_profile
        hc.save()
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.SUBMITTED, total_student_score=70)
        res = self.tp_service.approve_student_points_by_class(point, total_class_score=None)
        self.assertEqual(res.total_class_score, 70)

    def test_get_faculty_points_list_not_faculty(self):
        # Line 224
        self.tp_service.user = self.student
        with self.assertRaises(ValidationError):
            self.tp_service.get_faculty_points_list(self.semester)

    def test_get_faculty_points_list_no_faculty_org(self):
        # Line 228
        self.tp_service.user = self.org_officer
        self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
        self.org_officer.org_profile.faculty = None
        self.org_officer.org_profile.save()
        with self.assertRaises(ValidationError):
            self.tp_service.get_faculty_points_list(self.semester)

    def test_get_faculty_points_list_wrong_class(self):
        # Line 233
        self.tp_service.user = self.org_officer
        self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
        self.org_officer.org_profile.faculty = self.student.student_profile.faculty
        self.org_officer.org_profile.save()
        with self.assertRaises(ValidationError):
            self.tp_service.get_faculty_points_list(self.semester, class_id=99999)

    def test_approve_student_points_by_faculty_not_faculty(self):
        # Line 269
        self.tp_service.user = self.student
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester)
        with self.assertRaises(ValidationError):
            self.tp_service.approve_student_points_by_faculty(point)

    def test_approve_student_points_by_faculty_wrong_faculty(self):
        # Line 273
        self.tp_service.user = self.org_officer
        self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
        self.org_officer.org_profile.faculty = None
        self.org_officer.org_profile.save()
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester)
        with self.assertRaises(ValidationError):
            self.tp_service.approve_student_points_by_faculty(point)
            
    def test_approve_student_points_by_faculty_wrong_status(self):
        # Line 276
        self.tp_service.user = self.org_officer
        self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
        self.org_officer.org_profile.faculty = self.student.student_profile.faculty
        self.org_officer.org_profile.save()
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.SUBMITTED)
        with self.assertRaises(ValidationError):
            self.tp_service.approve_student_points_by_faculty(point)

    def test_approve_student_points_by_faculty_total_none(self):
        # Line 279
        self.tp_service.user = self.org_officer
        self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
        self.org_officer.org_profile.faculty = self.student.student_profile.faculty
        self.org_officer.org_profile.save()
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.CLASS_APPROVED, total_class_score=85)
        res = self.tp_service.approve_student_points_by_faculty(point, total_final_score=None)
        self.assertEqual(res.total_final_score, 85)

    def test_finance_get_campaigns_not_student(self):
        # Line 30
        res = self.finance_service.get_campaigns_for_user(self.org_officer)
        self.assertIsNotNone(res)

    def test_initiate_payment_not_student(self):
        # Line 46
        with self.assertRaises(ValidationError):
            self.finance_service.initiate_payment(self.org_officer, 1)

    def test_initiate_payment_no_campaign(self):
        # Line 51
        with self.assertRaises(Exception): # ResourceNotFoundError
            self.finance_service.initiate_payment(self.student, 99999)

    def test_get_class_finance_status_no_campaign(self):
        # Line 90
        with self.assertRaises(Exception): # ResourceNotFoundError
            self.finance_service.get_class_finance_status(self.student, 99999)

    def test_get_class_finance_status_no_class(self):
        # Line 99
        campaign = FeeCampaign.objects.create(title="T", amount=10, creator=self.org_officer, homeroom_class=None)
        # delete all homeroom classes to trigger
        HomeroomClass.objects.all().delete()
        with self.assertRaises(ValidationError):
            self.finance_service.get_class_finance_status(self.org_officer, campaign.id)

    def test_confirm_cash_payment_invalid(self):
        # Line 133
        with self.assertRaises(ValidationError):
            self.finance_service.confirm_cash_payment(self.bancansu, 9999, 9999)

    def test_toggle_payment_status_not_found(self):
        # Line 157
        with self.assertRaises(Exception): # ResourceNotFoundError
            self.finance_service.toggle_payment_status(self.bancansu, 9999, "SUCCESS")
