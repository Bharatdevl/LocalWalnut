import datetime

import pytest
from django.db import IntegrityError, connection

from company.models import Company, CompanyUsers
from employee.models import Employee
from scheduler import models


@pytest.fixture
def schedulesurvey_data():
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    models.ScheduleSurvey(
        schedule_time="12:00:00",
        weekday=models.WeekDays.MONDAY,
        company=company_obj,
    ).save()


def get_number_of_fields(model_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name = %s",
            (model_name,),
        )
        num_fields = cursor.fetchone()[0]
    return num_fields


def test_no_of_fields_schedulesurvey():
    assert len(models.ScheduleSurvey._meta.fields) == 5
    assert get_number_of_fields("scheduler_schedulesurvey") == 5


def test_schedulesurvey_list_empty():
    assert models.ScheduleSurvey.objects.count() == 0


def test_create_a_schedulesurvey(schedulesurvey_data):
    assert models.ScheduleSurvey.objects.count() == 1
    assert models.ScheduleSurvey.objects.latest(
        "id"
    ).schedule_time == datetime.time(12, 0)


def test_check_weekday(schedulesurvey_data):
    schedulesurvey_obj = models.ScheduleSurvey.objects.latest("id")
    assert schedulesurvey_obj.weekday == models.WeekDays.MONDAY


def test_unique_schedule_survey(schedulesurvey_data):
    # Try to create another ScheduleSurvey with the same combination
    with pytest.raises(IntegrityError):
        company_obj = Company.objects.latest("id")
        models.ScheduleSurvey.objects.create(
            schedule_time="12:00:00",
            weekday=models.WeekDays.MONDAY,
            company=company_obj,
        )


@pytest.fixture
def schedulecurriculum_data():
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    models.ScheduleCurriculum(
        schedule_time="12:00:00",
        weekday=models.WeekDays.MONDAY,
        company=company_obj,
    ).save()


def test_no_of_fields_schedulecurriculum():
    assert len(models.ScheduleCurriculum._meta.fields) == 5
    assert get_number_of_fields("scheduler_schedulecurriculum") == 5


def test_schedulecurriculum_list_empty():
    assert models.ScheduleCurriculum.objects.count() == 0


def test_create_a_schedulecurriculum(schedulecurriculum_data):
    assert models.ScheduleCurriculum.objects.count() == 1
    assert models.ScheduleCurriculum.objects.latest(
        "id"
    ).schedule_time == datetime.time(12, 0)


def test_check_weekday_in_curriculum(schedulecurriculum_data):
    schedulecurriculum_obj = models.ScheduleCurriculum.objects.latest("id")
    assert schedulecurriculum_obj.weekday == models.WeekDays.MONDAY


def test_unique_schedule_curriculm(schedulecurriculum_data):
    # Try to create another ScheduleCurriculum with the same combination
    with pytest.raises(IntegrityError):
        company_obj = Company.objects.latest("id")
        models.ScheduleCurriculum.objects.create(
            schedule_time="12:00:00",
            weekday=models.WeekDays.MONDAY,
            company=company_obj,
        )


@pytest.fixture
def schedulestatus_data():
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    models.ScheduleStatus(
        company=company_obj,
        question_schedule_counter=1,
    ).save()


def test_no_of_fields_schedulestatus():
    assert len(models.ScheduleStatus._meta.fields) == 3
    assert get_number_of_fields("scheduler_schedulestatus") == 3


def test_schedulestatus_list_empty():
    assert models.ScheduleStatus.objects.count() == 0


def test_create_a_schedulestatus(schedulestatus_data):
    assert models.ScheduleStatus.objects.count() == 1
    assert (
        models.ScheduleStatus.objects.latest("id").company.company_name
        == "abc company"
    )
