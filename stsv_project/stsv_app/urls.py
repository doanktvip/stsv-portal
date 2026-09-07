from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView, CustomTokenRefreshView, UserViewSet, AdminAccountViewSet,
    FacultyViewSet, OrgViewSet, SemesterViewSet, EventCategoryViewSet, EventViewSet,
    StudentSemesterPointViewSet, PointTransactionViewSet, TrainingRuleViewSet,
    FeeCampaignViewSet, PaymentViewSet, ClassFinanceManagementViewSet,
    SystemConfigViewSet, UserNotificationViewSet, SmartSearchView
)


app_name = "stsv_app"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("manage-accounts", AdminAccountViewSet, basename="admin-account")
router.register("faculties", FacultyViewSet, basename="faculty")
router.register("organizations", OrgViewSet, basename="organization")
router.register("semesters", SemesterViewSet, basename="semester")
router.register("event-categories", EventCategoryViewSet, basename="event-category")
router.register("events", EventViewSet, basename="event")
router.register("student-semester-points", StudentSemesterPointViewSet, basename="student-semester-point")
router.register("point-transactions", PointTransactionViewSet, basename="point-transaction")
router.register("training-rules", TrainingRuleViewSet, basename="training-rule")
router.register("finance/campaigns", FeeCampaignViewSet, basename="fee-campaign")
router.register("finance/payments", PaymentViewSet, basename="payment")
router.register("finance/class-management", ClassFinanceManagementViewSet, basename="class-finance-management")
router.register("system-configs", SystemConfigViewSet, basename="system-config")
router.register("notifications", UserNotificationViewSet, basename="notification")

urlpatterns = [
    path("auth/login", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("search/", SmartSearchView.as_view(), name="smart-search"),

    path("", include(router.urls)),
]
