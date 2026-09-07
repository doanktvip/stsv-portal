from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from stsv_app.exceptions import custom_exception_handler
from stsv_app.services import (
    ServiceError,
    ResourceNotFoundError,
    PermissionDeniedError,
)
import unittest.mock

class ExceptionsTestCase(TestCase):
    def test_custom_exception_handler_mapping(self):
        # 1. ResourceNotFoundError -> 404
        exc = ResourceNotFoundError("Not found")
        response = custom_exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_code"], "NOT_FOUND")

        # 2. PermissionDeniedError -> 403
        exc = PermissionDeniedError("Denied")
        response = custom_exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_code"], "PERMISSION_DENIED")

        # 3. ServiceError -> 500
        exc = ServiceError("Service error")
        response = custom_exception_handler(exc, {})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error_code"], "SERVER_ERROR")

        # 4. Method Not Allowed Mocking
        exc = unittest.mock.MagicMock()
        mock_response = Response(status=status.HTTP_405_METHOD_NOT_ALLOWED, data="Method Not Allowed")
        
        with unittest.mock.patch('stsv_app.exceptions.exception_handler', return_value=mock_response):
            response = custom_exception_handler(exc, {})
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            self.assertEqual(response.data["error_code"], "METHOD_NOT_ALLOWED")

        # 5. List data type mapping
        mock_response_list = Response(status=status.HTTP_400_BAD_REQUEST, data=["Error item"])
        with unittest.mock.patch('stsv_app.exceptions.exception_handler', return_value=mock_response_list):
            response = custom_exception_handler(exc, {})
            self.assertEqual(response.data["details"]["detail"], ["Error item"])
