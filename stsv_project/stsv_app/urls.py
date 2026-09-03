from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.events import EventCategoryViewSet, EventViewSet, YouthUnionRecordViewSet
from .views.users import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserViewSet, LecturerViewSet, OrgViewSet,
    AdminAccountViewSet
)
from .views.academics import StudentEducationProgramViewSet, SubjectViewSet, SemesterViewSet, CourseClassViewSet, \
    StudentCourseViewSet, ScheduleViewSet, StudentSemesterSummaryViewSet
from .views.core import FacultyViewSet, MajorViewSet, CohortViewSet
from .views.finance import FeeViewSet, PaymentViewSet, AdminFinanceViewSet, MockRedirectView
from .services.payments.webhooks import UnifiedWebhookView
from .views.system import SystemConfigViewSet, UserNotificationViewSet
from .views.support import ComplaintViewSet, FacilityReportViewSet
from .views.training_points import TrainingCriterionViewSet
from .views.search import SmartSearchView

app_name = "stsv_app"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("manage-accounts", AdminAccountViewSet, basename="admin-account")
router.register("faculties", FacultyViewSet, basename="faculty")
router.register("majors", MajorViewSet, basename="major")
router.register("cohorts", CohortViewSet, basename="cohort")
router.register("lecturers", LecturerViewSet, basename="lecturer")
router.register("organizations", OrgViewSet, basename="organization")
router.register("education-programs", StudentEducationProgramViewSet, basename="education-program")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("semesters", SemesterViewSet, basename="semester")
router.register("courses-classes", CourseClassViewSet, basename="course-class")
router.register("student-courses", StudentCourseViewSet, basename="student-course")
router.register("schedules", ScheduleViewSet, basename="schedule")
router.register("semester-summaries", StudentSemesterSummaryViewSet, basename="semester-summary")
router.register("event-categories", EventCategoryViewSet, basename="event-category")
router.register("events", EventViewSet, basename="event")
router.register("youth-union/records", YouthUnionRecordViewSet, basename="youth-union-record")
router.register("fees", FeeViewSet, basename="fee")
router.register("payments", PaymentViewSet, basename="payment")
router.register("admin-finance", AdminFinanceViewSet, basename="admin-finance")
router.register("system-configs", SystemConfigViewSet, basename="system-config")
router.register("notifications", UserNotificationViewSet, basename="notification")
router.register("complaints", ComplaintViewSet, basename="complaint")
router.register("facility-reports", FacilityReportViewSet, basename="facility-report")
router.register("training-criteria", TrainingCriterionViewSet, basename="training-criterion")

urlpatterns = [
    path("auth/login", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh", CustomTokenRefreshView.as_view(), name="token_refresh"),
    
    # Global Smart Search
    path("search/", SmartSearchView.as_view(), name="smart-search"),

    # Standalone Webhook cho các cổng thanh toán
    path("finance/webhook/<str:provider_name>/", UnifiedWebhookView.as_view(), name="finance-webhook"),
    path("payments/mock-redirect/", MockRedirectView.as_view(), name="mock-redirect"),

    path("", include(router.urls)),
]
