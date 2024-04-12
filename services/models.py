# Create your models here.
from django.db import models

from company.validators import NoAlphabetsValidator

# Create your models here.


class TwilioStatus(models.Model):
    sms_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255)
    employee_phone_number = models.CharField(
        max_length=20,
        validators=[
            NoAlphabetsValidator(limit_value=None),
        ],
    )
    from_number = models.CharField(
        max_length=20,
        validators=[
            NoAlphabetsValidator(limit_value=None),
        ],
    )
    error_code = models.CharField(max_length=255, blank=True, null=True)
    send_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "employee_phone_number",
                ]
            ),
        ]
