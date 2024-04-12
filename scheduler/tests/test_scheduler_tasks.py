# tests/test_scheduler_tasks.py
from unittest.mock import MagicMock, patch

import pytest
from celery import Celery
from celery.contrib.testing.worker import start_worker
from celery.result import AsyncResult
from django.utils import timezone

from company.models import Company, CompanyUsers
from employee.models import Employee
from scheduler.models import ScheduleStatus, ScheduleSurvey
from scheduler.tasks import send_curriculum_schedule, send_survey_questions
from survey.models import Question


# Celery application fixture
@pytest.fixture
def celery_app():
    app = Celery("test_scheduler_tasks")
    app.conf.update(
        broker_url="redis://localhost:6379",
        result_backend="redis://localhost:6379",
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
    )
    return app


@pytest.mark.skip(
    reason="Skipping test_send_survey_questions due to Celery worker dependency"
)
def test_send_survey_questions(celery_app):
    # Call the send_survey_questions task
    task_result = send_survey_questions.apply_async()
    # Wait for the task to complete
    result = task_result.get()

    # Check the task status
    assert (
        task_result.status == "SUCCESS"
    ), f"Task failed with status: {task_result.status}"

    # Check if the task was called
    assert (
        task_result.id
    )  # Check if the task has an ID (indicating it was called)

    # Check the task status
    assert (
        task_result.status == "SUCCESS"
    ), f"Task failed with status: {task_result.status}"


@pytest.fixture
def mock_redis_connection():
    with patch("scheduler.tasks.settings.REDIS_CURRICULUM_CONN") as mock_redis:
        yield mock_redis


@pytest.fixture
def mock_curriculum_schedule():
    return MagicMock(
        weekday="monday", schedule_time=MagicMock(hour=10, minute=30)
    )


@pytest.fixture
def mock_company():
    return MagicMock()


@pytest.fixture
def mock_curriculum_stack():
    return MagicMock()


@pytest.fixture
def mock_all_employees():
    return MagicMock()


@pytest.fixture
def mock_all_admins():
    return MagicMock()


@pytest.fixture
def mock_all_staff():
    return MagicMock()


@pytest.fixture
def mock_recipient():
    return MagicMock()


def test_send_curriculum_schedule(
    mock_redis_connection,
    mock_curriculum_schedule,
    mock_company,
    mock_curriculum_stack,
    mock_all_employees,
    mock_all_admins,
    mock_all_staff,
    mock_recipient,
):
    # Mock the return value of Redis connection
    mock_redis_connection.return_value = MagicMock()

    # Mock the return value of ScheduleCurriculum.objects.all()
    mock_curriculum_schedule.objects.all.return_value = [
        mock_curriculum_schedule
    ]

    # Mock the return value of CurriculumStack.objects.get()
    mock_curriculum_stack.curriculum_list.split.return_value = [
        "Curriculum 1",
        "Curriculum 2",
    ]

    # Mock the return values of Employee.objects.filter()
    mock_all_employees.filter.return_value = [mock_recipient]

    # Mock the return values of CompanyUsers.objects.filter() for admins and staff
    mock_all_admins.filter.return_value = []
    mock_all_staff.filter.return_value = []

    # Mock the behavior of util.is_queue_empty() and util.retrieve_message_from_redis()
    with patch(
        "scheduler.tasks.util.is_queue_empty"
    ) as mock_is_queue_empty, patch(
        "scheduler.tasks.util.retrieve_message_from_redis"
    ) as mock_retrieve_message, patch(
        "scheduler.tasks.util.store_messages_in_redis"
    ) as mock_store_messages:
        # Set up the return value for is_queue_empty() and retrieve_message_from_redis()
        mock_is_queue_empty.return_value = True
        mock_retrieve_message.return_value = "Test message"

        # Call the function under test
        send_curriculum_schedule()
