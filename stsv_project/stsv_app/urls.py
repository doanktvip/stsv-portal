from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.events import EventCategoryViewSet, EventViewSet, YouthUnionRecordViewSet
from .views.users import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserViewSet, LecturerViewSet, OrgViewSet,
)
from .views.academics import StudentEducationProgramViewSet, SubjectViewSet, SemesterViewSet, CourseClassViewSet, \
    StudentCourseViewSet, ScheduleViewSet
from .views.core import FacultyViewSet, MajorViewSet, CohortViewSet
from .views.finance import FeeViewSet, PaymentViewSet
from .views.system import SystemConfigViewSet

app_name = "stsv_app"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
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
router.register("event-categories", EventCategoryViewSet, basename="event-category")
router.register("events", EventViewSet, basename="event")
router.register("youth-union/records", YouthUnionRecordViewSet, basename="youth-union-record")
router.register("fees", FeeViewSet, basename="fee")
router.register("payments", PaymentViewSet, basename="payment")
router.register("system-configs", SystemConfigViewSet, basename="system-config")

urlpatterns = [
    path("auth/login", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh", CustomTokenRefreshView.as_view(), name="token_refresh"),

    path("", include(router.urls)),
]
