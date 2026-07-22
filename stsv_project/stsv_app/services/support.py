from .base import BaseService
from stsv_app.models.support import ServiceRequest, Complaint
from .exceptions import ResourceNotFoundError, ValidationError


class TicketService(BaseService):
    def create_service_request(
        self, student_id: int, service_type: str
    ) -> ServiceRequest:
        request = ServiceRequest(
            student_id=student_id,
            service_type=service_type,
            status=ServiceRequest.Status.PENDING,
        )
        request.save()
        return request

    def resolve_complaint(
        self, complaint_id: int, admin_id: int, response: str
    ) -> Complaint:
        try:
            complaint = Complaint.objects.get(id=complaint_id)
        except Complaint.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy khiếu nại.")

        if complaint.status == Complaint.Status.CLOSED:
            raise ValidationError("Khiếu nại này đã được đóng.")

        complaint.status = Complaint.Status.CLOSED
        complaint.resolved_by_id = admin_id  # type: ignore
        complaint.admin_response = response
        complaint.save()

        return complaint
