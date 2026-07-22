from django.db import transaction
from typing import Optional
from stsv_app.models.users import User


class BaseService:
    """
    Base class cho tất cả các services.
    Chứa các utilities dùng chung như quản lý database transaction và lưu trữ current user.
    """

    def __init__(self, user: Optional[User] = None):
        self.user = user

    @staticmethod
    def run_in_transaction(func):
        """Decorator để chạy một hàm trong một database transaction."""

        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)

        return wrapper
