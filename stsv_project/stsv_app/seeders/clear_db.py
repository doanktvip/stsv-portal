from django.db import connection
from stsv_app.models.core import Faculty, Major, Cohort, HomeroomClass
from stsv_app.models.academics import GradeConversionRule, Semester, Subject, EducationProgram, CourseClass, ScoreComponent, StudentCourse, StudentScoreDetail, Schedule, StudentSemesterSummary, IntegrationSyncLog
from stsv_app.models.users import User, StudentProfile, LecturerProfile, OrgProfile, UserDevice
from stsv_app.models.events import EventCategory, Event, CheckInSession, EventRegistration, YouthUnionRecord
from stsv_app.models.training_points import TrainingCriterion, StudentSemesterPoint, SemesterPointDetail, PointProof, PointHistory
from stsv_app.models.finance import Fee, Payment
from stsv_app.models.support import FacilityReport, Complaint
from stsv_app.models.system import SystemConfig, NotificationTemplate, UserNotification
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

def clear_database():
    """Xóa an toàn toàn bộ dữ liệu (trừ admin superuser) và reset ID."""
    # Vô hiệu hóa đồng bộ Elasticsearch để không bị lỗi ConnectionRefused
    settings.ELASTICSEARCH_DSL_AUTOSYNC = False

    # Xóa các model có ForeignKey phụ thuộc trước
    
    # System
    UserNotification.objects.all().delete()
    NotificationTemplate.objects.all().delete()
    SystemConfig.objects.all().delete()
    
    # Support
    Complaint.objects.all().delete()
    FacilityReport.objects.all().delete()
    
    # Finance
    Payment.objects.all().delete()
    Fee.objects.all().delete()
    
    # Training Points
    PointHistory.objects.all().delete()
    PointProof.objects.all().delete()
    SemesterPointDetail.objects.all().delete()
    StudentSemesterPoint.objects.all().delete()
    TrainingCriterion.objects.all().delete()
    
    # Events
    EventRegistration.objects.all().delete()
    CheckInSession.objects.all().delete()
    Event.objects.all().delete()
    EventCategory.objects.all().delete()
    YouthUnionRecord.objects.all().delete()
    
    # Academics
    IntegrationSyncLog.objects.all().delete()
    StudentSemesterSummary.objects.all().delete()
    Schedule.objects.all().delete()
    StudentScoreDetail.objects.all().delete()
    StudentCourse.objects.all().delete()
    ScoreComponent.objects.all().delete()
    CourseClass.objects.all().delete()
    EducationProgram.objects.all().delete()
    Subject.objects.all().delete()
    Semester.objects.all().delete()
    GradeConversionRule.objects.all().delete()
    
    # Users (Except superuser)
    UserDevice.objects.all().delete()
    StudentProfile.objects.all().delete()
    LecturerProfile.objects.all().delete()
    OrgProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    
    # Core
    HomeroomClass.objects.all().delete()
    Cohort.objects.all().delete()
    Major.objects.all().delete()
    Faculty.objects.all().delete()
    
    ContentType.objects.all().delete()

    # Reset AUTO_INCREMENT / IDs cho tất cả các bảng
    models_to_reset = [
        UserNotification, NotificationTemplate, SystemConfig,
        Complaint, FacilityReport, Payment, Fee,
        PointHistory, PointProof, SemesterPointDetail, StudentSemesterPoint, TrainingCriterion,
        EventRegistration, CheckInSession, Event, EventCategory, YouthUnionRecord,
        IntegrationSyncLog, StudentSemesterSummary, Schedule, StudentScoreDetail, StudentCourse,
        ScoreComponent, CourseClass, EducationProgram, Subject, Semester, GradeConversionRule,
        UserDevice, StudentProfile, LecturerProfile, OrgProfile, User,
        HomeroomClass, Cohort, Major, Faculty
    ]

    with connection.cursor() as cursor:
        if connection.vendor == 'mysql':
            for model in models_to_reset:
                cursor.execute(f"ALTER TABLE {model._meta.db_table} AUTO_INCREMENT = 1;")
        elif connection.vendor == 'sqlite':
            for model in models_to_reset:
                try:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{model._meta.db_table}';")
                except Exception:
                    pass
