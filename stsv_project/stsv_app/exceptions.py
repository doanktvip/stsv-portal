from rest_framework.views import exception_handler
from rest_framework import status, exceptions
from django.utils.translation import gettext_lazy as _
from stsv_app.services.exceptions import (
    ServiceError,
    ResourceNotFoundError,
    ValidationError,
    PermissionDeniedError,
)

# Cách chuẩn và Clean Code nhất: Ghi đè trực tiếp thông báo mặc định của DRF
exceptions.NotAuthenticated.default_detail = "Vui lòng cung cấp Token xác thực."
exceptions.PermissionDenied.default_detail = "Bạn không có quyền thực hiện hành động này."


def custom_exception_handler(exc, context):
    if isinstance(exc, ResourceNotFoundError):
        exc = exceptions.NotFound(detail=exc.message)
    elif isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(detail=exc.message)
    elif isinstance(exc, PermissionDeniedError):
        exc = exceptions.PermissionDenied(detail=exc.message)
    elif isinstance(exc, ServiceError):
        exc = exceptions.APIException(detail=exc.message)

    response = exception_handler(exc, context)

    if response is not None:
        error_code = "ERROR"
        message = _("Có lỗi xảy ra.")

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = "VALIDATION_ERROR"
            message = _("Lỗi xác thực dữ liệu")
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "UNAUTHORIZED"
            message = _("Chưa xác thực tài khoản")
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_code = "PERMISSION_DENIED"
            message = _("Bạn không có quyền thực hiện hành động này")
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "NOT_FOUND"
            message = _("Không tìm thấy tài nguyên")
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            error_code = "METHOD_NOT_ALLOWED"
            message = _("Phương thức HTTP không được hỗ trợ")
        elif response.status_code >= 500:
            error_code = "SERVER_ERROR"
            message = _("Lỗi hệ thống máy chủ")

        details_data = response.data
        if isinstance(details_data, list):
            details_data = {"detail": details_data}
        elif not isinstance(details_data, dict):
            details_data = {"detail": str(details_data)}

        formatted_response = {
            "status": "error",
            "message": str(message),
            "error_code": error_code,
            "details": details_data,
        }

        response.data = formatted_response

    return response
