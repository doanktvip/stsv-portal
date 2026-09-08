from django.urls import reverse
from .base import BaseAPITestCase
from stsv_app.models import Semester, StudentSemesterPoint, OrgProfile, FeeCampaign
from unittest.mock import patch
from rest_framework.exceptions import ValidationError as VlError
from stsv_app.services import ResourceNotFoundError, ValidationError

class ViewsEdgeCasesTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.semester = Semester.objects.first()

    def test_training_points_my_points_no_semester(self):
        self.client.force_authenticate(user=self.student)
        Semester.objects.all().delete()
        url = reverse('stsv_app:student-semester-point-my-points')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_training_points_submit_no_semester(self):
        self.client.force_authenticate(user=self.student)
        Semester.objects.all().delete()
        url = reverse('stsv_app:student-semester-point-submit')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_training_points_class_list_no_semester(self):
        self.client.force_authenticate(user=self.bancansu)
        if hasattr(self.student, 'student_profile') and hasattr(self.bancansu, 'student_profile'):
            self.student.student_profile.homeroom_class.president = self.bancansu.student_profile
            self.student.student_profile.homeroom_class.save()
        Semester.objects.all().delete()
        url = reverse('stsv_app:student-semester-point-class-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_training_points_open_evaluation_no_semester(self):
        self.client.force_authenticate(user=self.org_officer)
        if hasattr(self.org_officer, 'org_profile'):
            self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
            self.org_officer.org_profile.faculty = self.student.student_profile.faculty
            self.org_officer.org_profile.save()
        Semester.objects.all().delete()
        url = reverse('stsv_app:student-semester-point-open-evaluation')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_training_points_faculty_list_no_semester(self):
        self.client.force_authenticate(user=self.org_officer)
        if hasattr(self.org_officer, 'org_profile'):
            self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
            self.org_officer.org_profile.faculty = self.student.student_profile.faculty
            self.org_officer.org_profile.save()
        Semester.objects.all().delete()
        url = reverse('stsv_app:student-semester-point-faculty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch('stsv_app.services.TrainingPointService.calculate_student_points')
    def test_my_points_exception(self, mock_calc):
        mock_calc.side_effect = Exception("Test Error")
        self.client.force_authenticate(user=self.student)
        url = reverse('stsv_app:student-semester-point-my-points')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.services.TrainingPointService.submit_student_points')
    def test_submit_exception(self, mock_submit):
        mock_submit.side_effect = ValidationError("Validation Error")
        self.client.force_authenticate(user=self.student)
        url = reverse('stsv_app:student-semester-point-submit')
        response = self.client.post(url, {'points_data': {}}, format='json')
        self.assertEqual(response.status_code, 400)
        
        mock_submit.side_effect = Exception("General Error")
        response = self.client.post(url, {'points_data': {}}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_submit_is_draft(self):
        self.client.force_authenticate(user=self.student)
        self.semester.is_evaluation_open = True
        self.semester.save()
        StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.DRAFT)
        url = reverse('stsv_app:student-semester-point-submit')
        response = self.client.post(url, {'semester_id': self.semester.id, 'is_draft': True, 'points_data': {'categories': []}, 'total_student_score': 85}, format='json')
        self.assertEqual(response.status_code, 200)

    @patch('stsv_app.services.TrainingPointService.get_class_points_list')
    def test_class_list_exception(self, mock_list):
        mock_list.side_effect = VlError("Validation Error")
        self.client.force_authenticate(user=self.bancansu)
        if hasattr(self.student, 'student_profile') and hasattr(self.bancansu, 'student_profile'):
            self.student.student_profile.homeroom_class.president = self.bancansu.student_profile
            self.student.student_profile.homeroom_class.save()
            
        url = reverse('stsv_app:student-semester-point-class-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        mock_list.side_effect = Exception("General Error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.services.TrainingPointService.approve_student_points_by_class')
    def test_class_approve_exception(self, mock_approve):
        mock_approve.side_effect = ValidationError("Validation Error")
        self.client.force_authenticate(user=self.bancansu)
        if hasattr(self.bancansu, 'student_profile'):
            self.bancansu.student_profile.homeroom_class.president = self.bancansu.student_profile
            self.bancansu.student_profile.homeroom_class.save()
            
            point = StudentSemesterPoint.objects.create(student=self.bancansu.student_profile, semester=self.semester)
            url = reverse('stsv_app:student-semester-point-class-approve', args=[point.id])
            response = self.client.post(url, {}, format='json')
            self.assertEqual(response.status_code, 400)

            mock_approve.side_effect = Exception("General Error")
            response = self.client.post(url, {}, format='json')
            self.assertEqual(response.status_code, 400)

    def test_class_approve_is_draft(self):
        self.client.force_authenticate(user=self.bancansu)
        if hasattr(self.bancansu, 'student_profile'):
            self.bancansu.student_profile.homeroom_class.president = self.bancansu.student_profile
            self.bancansu.student_profile.homeroom_class.save()

            point = StudentSemesterPoint.objects.create(student=self.bancansu.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.SUBMITTED)
            url = reverse('stsv_app:student-semester-point-class-approve', args=[point.id])
            response = self.client.post(url, {'is_draft': True}, format='json')
            self.assertEqual(response.status_code, 200)

    @patch('stsv_app.services.TrainingPointService.open_evaluation')
    def test_open_evaluation_exception(self, mock_open):
        mock_open.side_effect = VlError("Validation Error")
        self.client.force_authenticate(user=self.org_officer)
        if hasattr(self.org_officer, 'org_profile'):
            self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
            self.org_officer.org_profile.faculty = self.student.student_profile.faculty
            self.org_officer.org_profile.save()
        
        url = reverse('stsv_app:student-semester-point-open-evaluation')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 403)

        mock_open.side_effect = Exception("General Error")
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.services.TrainingPointService.get_faculty_points_list')
    def test_faculty_list_exception(self, mock_list):
        mock_list.side_effect = VlError("Validation Error")
        self.client.force_authenticate(user=self.org_officer)
        if hasattr(self.org_officer, 'org_profile'):
            self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
            self.org_officer.org_profile.faculty = self.student.student_profile.faculty
            self.org_officer.org_profile.save()
            
        url = reverse('stsv_app:student-semester-point-faculty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        mock_list.side_effect = Exception("General Error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.services.TrainingPointService.approve_student_points_by_faculty')
    def test_faculty_approve_exception(self, mock_approve):
        mock_approve.side_effect = ValidationError("Validation Error")
        self.client.force_authenticate(user=self.org_officer)
        if hasattr(self.org_officer, 'org_profile'):
            self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
            self.org_officer.org_profile.faculty = self.student.student_profile.faculty
            self.org_officer.org_profile.save()
            
        # The view for faculty_approve does not filter by student__user=user, since ORGOFFICER bypasses it.
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester)
        url = reverse('stsv_app:student-semester-point-faculty-approve', args=[point.id])
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

        mock_approve.side_effect = Exception("General Error")
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_faculty_approve_is_draft(self):
        self.client.force_authenticate(user=self.org_officer)
        self.org_officer.org_profile.org_type = OrgProfile.OrgType.FACULTY
        self.org_officer.org_profile.faculty = self.student.student_profile.faculty
        self.org_officer.org_profile.save()
        point = StudentSemesterPoint.objects.create(student=self.student.student_profile, semester=self.semester, status=StudentSemesterPoint.Status.CLASS_APPROVED)
        url = reverse('stsv_app:student-semester-point-faculty-approve', args=[point.id])
        response = self.client.post(url, {'is_draft': True}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_point_transaction_queryset_semester_id(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('stsv_app:point-transaction-list')
        response = self.client.get(url, {'semester_id': self.semester.id})
        self.assertEqual(response.status_code, 200)

    def test_point_transaction_perform_create_no_semester(self):
        self.client.force_authenticate(user=self.student)
        Semester.objects.all().delete()
        url = reverse('stsv_app:point-transaction-list')
        response = self.client.post(url, {'points_changed': 10, 'reason': 'test'}, format='json')
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.views.finance.hasattr')
    def test_payment_viewset_queryset_none(self, mock_hasattr):
        mock_hasattr.return_value = False
        self.client.force_authenticate(user=self.student)
        url = reverse('stsv_app:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results', [])), 0)

    @patch('stsv_app.services.FinanceService.initiate_payment')
    def test_payment_create_exceptions(self, mock_init):
        mock_init.side_effect = ResourceNotFoundError("Error")
        self.client.force_authenticate(user=self.student)
        campaign = FeeCampaign.objects.create(title="C1", amount=10, creator=self.bancansu)
        url = reverse('stsv_app:payment-list')
        response = self.client.post(url, {'campaign': campaign.id, 'amount': 10, 'payment_method': 'VIETQR'}, format='json')
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.services.FinanceService.get_class_finance_status')
    def test_class_finance_status_exceptions(self, mock_status):
        self.client.force_authenticate(user=self.bancansu)
        url = reverse('stsv_app:class-finance-management-class-status', args=[999])
        
        mock_status.side_effect = ResourceNotFoundError("Error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        mock_status.side_effect = ValidationError("Error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    @patch('stsv_app.services.FinanceService.toggle_payment_status')
    def test_toggle_payment_exceptions(self, mock_toggle):
        mock_toggle.side_effect = ResourceNotFoundError("Error")
        self.client.force_authenticate(user=self.bancansu)
        url = reverse('stsv_app:class-finance-management-toggle-payment', args=[999])
        response = self.client.post(url, {'status': 'SUCCESS'}, format='json')
        self.assertEqual(response.status_code, 404)

    @patch('stsv_app.services.FinanceService.confirm_cash_payment')
    def test_confirm_cash_exceptions(self, mock_confirm):
        mock_confirm.side_effect = ValidationError("Error")
        self.client.force_authenticate(user=self.bancansu)
        url = reverse('stsv_app:class-finance-management-confirm-cash')
        response = self.client.post(url, {'campaign_id': 999, 'student_id': 999}, format='json')
        self.assertEqual(response.status_code, 400)
