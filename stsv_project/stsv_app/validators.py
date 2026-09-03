import re
from django.core.exceptions import ValidationError


class CustomMinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"Mật khẩu này quá ngắn. Nó phải chứa ít nhất {self.min_length} ký tự.",
                code="password_too_short",
            )

    def get_help_text(self):
        return f"Mật khẩu của bạn phải chứa ít nhất {self.min_length} ký tự."


class NoVietnameseCharactersValidator:
    def validate(self, password, user=None):
        if not password.isascii():
            raise ValidationError(
                "Mật khẩu không được chứa ký tự Tiếng Việt có dấu hoặc ký tự lạ.",
                code="password_has_unicode",
            )

    def get_help_text(self):
        return "Mật khẩu chỉ được chứa các ký tự chữ cái không dấu, số và ký tự đặc biệt cơ bản."
