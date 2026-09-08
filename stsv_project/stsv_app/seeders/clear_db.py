from django.db import connection
from stsv_app.models import Faculty, HomeroomClass, Semester, User, StudentProfile, OrgProfile, EventCategory, Event, CheckInSession, EventRegistration, StudentSemesterPoint, PointTransaction, TrainingCriterion, TrainingRule, FeeCampaign, Payment, SystemConfig, NotificationTemplate, UserNotification
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

def clear_database():
    # Vô hiệu hóa đồng bộ Elasticsearch để không bị lỗi ConnectionRefused
    settings.ELASTICSEARCH_DSL_AUTOSYNC = False

    # Xóa các model có ForeignKey phụ thuộc trước
    
    # System
    UserNotification.objects.all().delete()
    NotificationTemplate.objects.all().delete()
    SystemConfig.objects.all().delete()
    
    # Finance
    Payment.objects.all().delete()
    FeeCampaign.objects.all().delete()
    
    # Training Points
    PointTransaction.objects.all().delete()
    StudentSemesterPoint.objects.all().delete()
    TrainingRule.objects.all().delete()
    TrainingCriterion.objects.all().delete()
    
    # Events
    EventRegistration.objects.all().delete()
    CheckInSession.objects.all().delete()
    Event.objects.all().delete()
    EventCategory.objects.all().delete()
    
    # Academics
    Semester.objects.all().delete()
    
    # Users (Except superuser)
    StudentProfile.objects.all().delete()
    OrgProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    
    # Core
    HomeroomClass.objects.all().delete()
    Faculty.objects.all().delete()
    
    ContentType.objects.all().delete()

    # Reset AUTO_INCREMENT / IDs cho tất cả các bảng
    models_to_reset = [
        UserNotification, NotificationTemplate, SystemConfig,
        Payment, FeeCampaign,
        PointTransaction, StudentSemesterPoint, TrainingRule, TrainingCriterion,
        EventRegistration, CheckInSession, Event, EventCategory,
        Semester,
        StudentProfile, OrgProfile, User,
        HomeroomClass, Faculty
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
