from .base import BaseService
from stsv_app.models.training_points import StudentSemesterPoint, PointProof, TrainingCriterion
from .exceptions import ResourceNotFoundError, ValidationError

class TrainingPointService(BaseService):
    def get_semester_points(self, student_profile_id: int, semester_id: int) -> StudentSemesterPoint:
        try:
            return StudentSemesterPoint.objects.get(student_id=student_profile_id, semester_id=semester_id)
        except StudentSemesterPoint.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy dữ liệu điểm rèn luyện của sinh viên trong kỳ này.")
            
    def submit_point_proof(self, student_profile_id: int, semester_id: int, criterion_id: int, file_url: str, activity_name: str) -> PointProof:
        try:
            criterion = TrainingCriterion.objects.get(id=criterion_id)
        except TrainingCriterion.DoesNotExist:
            raise ResourceNotFoundError("Không tìm thấy tiêu chí điểm rèn luyện này.")
            
        proof = PointProof(
            student_id=student_profile_id,
            semester_id=semester_id,
            criterion=criterion,
            activity_name=activity_name,
            file_url=file_url,
            status=PointProof.Status.PENDING
        )
        proof.save()
        return proof
