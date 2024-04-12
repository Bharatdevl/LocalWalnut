import uuid

from django.contrib.auth.models import User
from django.db import models

from .validators import NoAlphabetsValidator


class Company(models.Model):
    company_name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Automatically set on creation
    updated_at = models.DateTimeField(
        auto_now=True
    )  # Automatically set on each update

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        indexes = [models.Index(fields=["company_name"])]

    def __str__(self):
        return self.company_name


class CompanyUsers(models.Model):
    """
    CompanyUsers is the model which includes data model for company
    admin and staff who will be the user of the walnuteq management
    application/dashboard
    **CompanyUsers are not Employees in perspective to walnuteq application**
    """

    class AccessRole(models.TextChoices):
        COMPANY_ADMIN = "company_admin", "company_admin"
        COMPANY_STAFF = "company_staff", "company_staff"

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="company_users"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            NoAlphabetsValidator(limit_value=None),
        ],
    )
    email = models.EmailField(unique=True, max_length=255)
    department = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    access_role = models.CharField(max_length=20, choices=AccessRole.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_opted = models.BooleanField(default=True)
    employee_queue_key = models.UUIDField(default=uuid.uuid4)

    class Meta:
        verbose_name = "Company Users"
        verbose_name_plural = "Company Users"
        indexes = [
            models.Index(
                fields=[
                    "phone_number",
                ]
            ),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.company} | {self.email}"
