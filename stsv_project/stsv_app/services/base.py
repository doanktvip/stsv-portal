from django.db import transaction
from typing import Optional
from stsv_app.models import User


class BaseService:
    def __init__(self, user: Optional[User] = None):
        self.user = user

    @staticmethod
    def run_in_transaction(func):
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)

        return wrapper
