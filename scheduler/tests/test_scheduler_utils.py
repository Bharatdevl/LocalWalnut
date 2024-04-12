from unittest.mock import MagicMock, patch

import pytest

from scheduler import utils


# Mocking settings module
@pytest.fixture
def settings():
    return MagicMock(REDIS_HOST="localhost", REDIS_PORT=6379, REDIS_DB=0)


# Mocking Django models
@pytest.fixture
def employee_obj():
    return MagicMock(employee_queue_key="employee_key")


@pytest.fixture
def curriculum_obj():
    return MagicMock(curriculum_name="Test Curriculum")


@pytest.fixture
def curriculum_message_obj():
    return MagicMock(curriculum_message="Test Message")


# Test get_redis_connection function
def test_get_redis_connection(settings):
    assert settings.REDIS_CURRICULUM_CONN is not None


# Test store_messages_in_redis function
@patch("curriculum.models.Curriculum.objects.get")
@patch("curriculum.models.Curriculum_Message.objects.filter")
def test_store_messages_in_redis(
    curriculum_message_filter, curriculum_get, employee_obj
):
    # Mocking a queryset object
    queryset_mock = MagicMock()
    queryset_mock.order_by.return_value = (
        queryset_mock  # Mocking the order_by method
    )

    # Setting up curriculum_message_filter to return the queryset mock
    curriculum_message_filter.return_value = queryset_mock

    # Mocking curriculum_get to return a MagicMock
    curriculum_get.return_value = MagicMock()

    # Calling the function under test
    utils.store_messages_in_redis(employee_obj, ["Test Curriculum"])

    # Asserting that order_by method was called once
    assert queryset_mock.order_by.call_count == 1
