from .base import BaseAPITestCase
from stsv_app.models import StudentSemesterPoint, Semester, OrgProfile, Payment, FeeCampaign
from stsv_app.services import TrainingPointService, FinanceService

class FullCoverageAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.semester = Semester.objects.first()
        self.tp_service = TrainingPointService()
        self.finance_service = FinanceService()

    def test_calculate_student_points_full(self):
        self.tp_service.user = self.student
        if self.semester and hasattr(self.student, 'student_profile'):
            res = self.tp_service.calculate_student_points(self.semester)
            self.assertIsNotNone(res)

    def test_submit_student_points_full(self):
        self.tp_service.user = self.student
        if self.semester and hasattr(self.student, 'student_profile'):
            self.semester.is_evaluation_open = True
            self.semester.save()
            point, _ = StudentSemesterPoint.objects.get_or_create(
                student=self.student.student_profile,
                semester=self.semester,
                defaults={'status': StudentSemesterPoint.Status.DRAFT}
            )
            point.status = StudentSemesterPoint.Status.DRAFT
            point.save()
            pt = self.tp_service.submit_student_points(
                self.semester,
                points_data={'categories': []},
                total_student_score=85,
                is_draft=False
            )
            self.assertEqual(pt.total_student_score, 85)


    def test_approve_student_points_by_class(self):
        # Make bancansu president of student's homeroom class
        if hasattr(self.student, 'student_profile'):
            hc = self.student.student_profile.homeroom_class
            if hc and hasattr(self.bancansu, 'student_profile'):
                hc.president = self.bancansu.student_profile
                hc.save()

        self.tp_service.user = self.bancansu
        if self.semester and hasattr(self.student, 'student_profile'):
            point, _ = StudentSemesterPoint.objects.get_or_create(
                student=self.student.student_profile,
                semester=self.semester
            )
            point.status = StudentSemesterPoint.Status.SUBMITTED
            point.save()
            res = self.tp_service.approve_student_points_by_class(
                point,
                total_class_score=88,
                class_points_data={},
                is_draft=False
            )
            self.assertEqual(res.status, StudentSemesterPoint.Status.CLASS_APPROVED)

    def test_open_evaluation_and_faculty_approve(self):
        # Set org_officer to FACULTY org
        if hasattr(self.org_officer, 'org_profile') and hasattr(self.student, 'student_profile'):
            org = self.org_officer.org_profile
            org.org_type = OrgProfile.OrgType.FACULTY
            org.faculty = self.student.student_profile.faculty
            org.save()

        self.tp_service.user = self.org_officer
        if self.semester:
            self.tp_service.open_evaluation(self.semester)
            self.semester.refresh_from_db()
            self.assertTrue(self.semester.is_evaluation_open)

        if self.semester and hasattr(self.student, 'student_profile'):
            point, _ = StudentSemesterPoint.objects.get_or_create(
                student=self.student.student_profile,
                semester=self.semester
            )
            point.status = StudentSemesterPoint.Status.CLASS_APPROVED
            point.save()
            res = self.tp_service.approve_student_points_by_faculty(
                point,
                total_final_score=90,
                faculty_points_data={},
                is_draft=False
            )
            self.assertEqual(res.status, StudentSemesterPoint.Status.FACULTY_APPROVED)

    def test_get_class_points_list(self):
        if hasattr(self.bancansu, 'student_profile') and hasattr(self.student, 'student_profile'):
            hc = self.student.student_profile.homeroom_class
            if hc:
                hc.president = self.bancansu.student_profile
                hc.save()
        self.tp_service.user = self.bancansu
        if self.semester:
            class_name, points = self.tp_service.get_class_points_list(self.semester)
            self.assertIsNotNone(class_name)

    def test_get_faculty_points_list(self):
        if hasattr(self.org_officer, 'org_profile') and hasattr(self.student, 'student_profile'):
            org = self.org_officer.org_profile
            org.org_type = OrgProfile.OrgType.FACULTY
            org.faculty = self.student.student_profile.faculty
            org.save()
        self.tp_service.user = self.org_officer
        if self.semester:
            data, is_points = self.tp_service.get_faculty_points_list(self.semester)
            self.assertIsNotNone(data)
            # also test class_id filter branch
            if hasattr(self.student, 'student_profile') and self.student.student_profile.homeroom_class:
                pts, is_pts = self.tp_service.get_faculty_points_list(self.semester, class_id=self.student.student_profile.homeroom_class.id)
                self.assertTrue(is_pts)


    def test_finance_service_full(self):
        campaign = FeeCampaign.objects.first()
        if campaign and hasattr(self.student, 'student_profile'):
            payment = self.finance_service.confirm_cash_payment(
                user=self.bancansu,
                campaign_id=campaign.id,
                student_id=self.student.student_profile.id,
                notes="Đã thu tiền mặt"
            )
            self.assertEqual(payment.status, Payment.Status.SUCCESS)

            toggled = self.finance_service.toggle_payment_status(
                user=self.bancansu,
                payment_id=payment.id,
                target_status=Payment.Status.PENDING,
                notes="Hủy thanh toán"
            )
            self.assertEqual(toggled.status, Payment.Status.PENDING)

