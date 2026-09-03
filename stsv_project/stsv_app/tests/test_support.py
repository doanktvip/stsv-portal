from rest_framework import status
from django.urls import reverse
from stsv_app.tests.base import BaseAPITestCase
from stsv_app.models.support import Complaint, FacilityReport
import tempfile

class ComplaintAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.complaint = Complaint.objects.create(
            reporter=self.student,
            title="Mạng wifi yếu",
            description="Wifi thư viện quá yếu",
            priority="HIGH",
            status="PENDING"
        )
        
    def test_student_get_complaints(self):
        url = reverse('stsv_app:complaint-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vì student có 1 complaint
        data_list = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(data_list), 1)

    def test_admin_get_complaints(self):
        url = reverse('stsv_app:complaint-list')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_list = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(data_list), 1)
        
    def test_student_create_complaint(self):
        url = reverse('stsv_app:complaint-list')
        self.client.force_authenticate(user=self.student)
        data = {
            "title": "Nhà vệ sinh dơ",
            "description": "Cần dọn vệ sinh",
            "priority": "MEDIUM"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_resolve_complaint_forbidden(self):
        url = reverse('stsv_app:complaint-resolve-complaint', kwargs={'pk': self.complaint.pk})
        self.client.force_authenticate(user=self.student)
        data = {"admin_response": "Đã sửa"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_resolve_complaint_success(self):
        url = reverse('stsv_app:complaint-resolve-complaint', kwargs={'pk': self.complaint.pk})
        self.client.force_authenticate(user=self.admin)
        data = {"admin_response": "Đã ghi nhận và xử lý"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, "CLOSED")

    def test_admin_resolve_complaint_missing_response(self):
        url = reverse('stsv_app:complaint-resolve-complaint', kwargs={'pk': self.complaint.pk})
        self.client.force_authenticate(user=self.admin)
        data = {"admin_response": ""}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class FacilityReportAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.report = FacilityReport.objects.create(
            reporter=self.student,
            room="A1-101",
            description="Bóng đèn hỏng",
            priority="LOW",
            status="PENDING"
        )
        
    def test_student_get_reports(self):
        url = reverse('stsv_app:facility-report-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_create_report(self):
        url = reverse('stsv_app:facility-report-list')
        self.client.force_authenticate(user=self.student)
        data = {
            "room": "B2-202",
            "description": "Máy lạnh chảy nước",
            "priority": "HIGH"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_resolve_report_success(self):
        url = reverse('stsv_app:facility-report-resolve-report', kwargs={'pk': self.report.pk})
        self.client.force_authenticate(user=self.admin)
        # Giả lập upload ảnh
        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        
        # Mặc dù request test không thực sự upload file vật lý, nhưng gửi 1 chuỗi cũng giúp test logic view
        data = {"resolution_image": image}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "RESOLVED")
