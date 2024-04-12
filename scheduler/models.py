from django.db import models

from company.models import Company, CompanyUsers
from employee.models import Employee


class WeekDays(models.TextChoices):
    MONDAY = "monday", "Monday"
    TUESDAY = "tuesday", "Tuesday"
    WEDNESDAY = "wednesday", "Wednesday"
    THURSDAY = "thursday", "Thursday"
    FRIDAY = "friday", "Friday"
    SATURDAY = "saturday", "Saturday"
    SUNDAY = "sunday", "Sunday"


class ScheduleSurvey(models.Model):
    """
    Model to represent the schedule Survey for a company.
    Each entry should have a unique combination of company, schedule_time, and weekday.
    """

    schedule_time = models.TimeField()
    weekday = models.CharField(
        max_length=10, blank=True, null=True, choices=WeekDays.choices
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta class to ensure uniqueness of company, schedule_time, and weekday together.
        """

        unique_together = ["schedule_time", "weekday", "company"]


class ScheduleStatus(models.Model):

    """Model to represent the schedule status for a company, particularly for managing scheduled survey questions"""

    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name="schedule_status"
    )
    question_schedule_counter = models.IntegerField(
        default=0, blank=True, null=True
    )


class ScheduleCurriculum(models.Model):
    """
    Model to represent the schedule curriculum for a company.
    Each entry should have a unique combination of company, schedule_time, and weekday.
    """

    schedule_time = models.TimeField()
    weekday = models.CharField(
        max_length=10, blank=True, null=True, choices=WeekDays.choices
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta class to ensure uniqueness of company, schedule_time, and weekday together.
        """

        unique_together = ["schedule_time", "weekday", "company"]
