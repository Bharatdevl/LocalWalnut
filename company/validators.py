from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator


class NoAlphabetsValidator(BaseValidator):
    message = "This field cannot contain alphabetic characters"
    code = "no_alphabets"

    def compare(self, value, limit_value):
        if any(char.isalpha() for char in value):
            raise ValidationError(self.message, code=self.code)
