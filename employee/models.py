import uuid

from django.db import models

from company.models import Company
from company.validators import NoAlphabetsValidator
from survey.models import Question


class Employee(models.Model):
    """
    Employee model has been created and have a following fields
    """

    first_name = models.CharField(max_length=225)
    middle_name = models.CharField(max_length=225, blank=True, null=True)
    last_name = models.CharField(max_length=225)
    phone_number = models.BigIntegerField(
        unique=True,
        validators=[
            NoAlphabetsValidator,
        ],
    )
    email = models.CharField(unique=True, max_length=225)
    department = models.CharField(max_length=225, blank=True, null=True)
    job_title = models.CharField(max_length=225, blank=True, null=True)
    location = models.CharField(max_length=225, blank=True, null=True)
    language = models.CharField(max_length=225, blank=True, null=True)
    company = models.ForeignKey(
        Company,
        related_name="employee_company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    supervisor = models.CharField(max_length=225, blank=True, null=True)
    is_opted = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Automatically set on creation
    updated_at = models.DateTimeField(
        auto_now=True
    )  # Automatically set on each update
    employee_queue_key = models.UUIDField(default=uuid.uuid4)

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
        ]

    def __str__(self):
        return f"{self.email} | {self.phone_number}"


class EmployeeRating(models.Model):
    """
    EmployeeRating model having the following fields and a relationship with the company
    and on a particular question, an employee gives a rating by replying to a question.
    """

    company = models.ForeignKey(
        Company, related_name="rating_company", on_delete=models.CASCADE
    )
    employee_phone_number = models.CharField(max_length=12)
    question = models.ForeignKey(
        Question, related_name="rating_question", on_delete=models.CASCADE
    )
    send_timestamp = models.DateTimeField(auto_now_add=True)
    sms_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255)
    rating = models.IntegerField(blank=True, null=True)
    expire_timestamp = models.DateTimeField(auto_now_add=True)
