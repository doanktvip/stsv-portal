from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Sổ Tay Sinh Viên API",
        default_version="v1",
        description="Tài liệu các đường dẫn API cho ứng dụng Mobile Sổ Tay Sinh Viên",
        contact=openapi.Contact(email="2351050031doan@ou.edu.vn"),
        license=openapi.License(name="Nguyễn Văn Đoàn"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", include("stsv_app.urls")),
    path("admin/", admin.site.urls),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
