from django.test import TestCase
from django.core.exceptions import ValidationError
from stsv_app.validators import CustomMinimumLengthValidator, NoVietnameseCharactersValidator

class ValidatorsTestCase(TestCase):
    def test_minimum_length_validator(self):
        validator = CustomMinimumLengthValidator(min_length=8)
        
        # Hợp lệ
        validator.validate("12345678")
        
        # Không hợp lệ
        with self.assertRaises(ValidationError) as context:
            validator.validate("1234567")
        self.assertEqual(context.exception.code, "password_too_short")
        
        # Test help text
        help_text = validator.get_help_text()
        self.assertIn("Mật khẩu của bạn phải chứa ít nhất 8 ký tự.", help_text)

    def test_no_vietnamese_characters_validator(self):
        validator = NoVietnameseCharactersValidator()
        
        # Hợp lệ
        validator.validate("password123")
        validator.validate("P@ssw0rd!")
        
        # Không hợp lệ (Có dấu Tiếng Việt)
        with self.assertRaises(ValidationError) as context:
            validator.validate("mậtkhẩu123")
        self.assertEqual(context.exception.code, "password_has_unicode")
        
        # Test help text
        help_text = validator.get_help_text()
        self.assertIn("Mật khẩu chỉ được chứa các ký tự chữ cái không dấu", help_text)
