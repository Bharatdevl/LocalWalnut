import os
import subprocess
import uuid

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError

from company.models import Company
from curriculum.models import *


@pytest.fixture
def company_data():
    Company(company_name="Test Company").save()
    return Company.objects.latest("id")


@pytest.fixture
def curriculum_data(company_data):
    return Curriculum.objects.create(curriculum_name="Test Curriculum")


@pytest.fixture
def curriculum_message_data(curriculum_data):
    return Curriculum_Message.objects.create(
        curriculum=curriculum_data,
        curriculum_message="Test Message",
        curriculum_index=1,
    )


def test_create_curriculum(curriculum_data):
    assert Curriculum.objects.count() == 1
    assert Curriculum.objects.get(curriculum_name="Test Curriculum")


def test_unique_curriculum_name(curriculum_data):
    with pytest.raises(IntegrityError):
        Curriculum.objects.create(curriculum_name="Test Curriculum")


def test_create_curriculum_message(curriculum_message_data):
    assert Curriculum_Message.objects.count() == 1
    assert Curriculum_Message.objects.get(curriculum_message="Test Message")


def test_upload_curriculum_file_invalid_encoding():
    # Create a Curriculum instance
    curriculum = Curriculum.objects.create(curriculum_name="Test Curriculum")

    # Create a sample non-UTF-8 encoded CSV file for testing
    file_content = "Index,Message\n1,Test Message 1\n2,Test Message 2"
    non_utf8_csv_file = SimpleUploadedFile(
        "non_utf8_test_file.csv", file_content.encode("latin-1")
    )

    # Create an UploadCurriculumfile instance with the non-UTF-8 encoded file
    upload_file = UploadCurriculumfile.objects.create(
        curriculum_name=curriculum, file_name=non_utf8_csv_file
    )

    # Attempt to run the clean method and expect a ValidationError
    with pytest.raises(ValidationError) as exc_info:
        upload_file.clean()

    # Check if the specific error message is present
    assert "File encoding must be UTF-8" in str(exc_info.value)


def test_upload_curriculum_file_valid_encoding():
    # Create a Curriculum instance
    curriculum = Curriculum.objects.create(curriculum_name="Test Curriculum")

    # Create a sample UTF-8 encoded CSV file for testing
    utf8_content = "Index,Message\n1,नम\n2,こん"
    utf8_csv_file = SimpleUploadedFile(
        "utf8_test_file.csv", utf8_content.encode("utf-8")
    )

    upload_file = UploadCurriculumfile.objects.create(
        curriculum_name=curriculum, file_name=utf8_csv_file
    )

    try:
        upload_file.clean()
    except ValidationError as e:
        pytest.fail(f"Unexpected ValidationError: {e}")

    # Check if Curriculum_Message objects were created
    assert Curriculum_Message.objects.count() == 2

    # Check if the Curriculum_Message objects have the correct values
    message_objects = Curriculum_Message.objects.all()
    assert message_objects[0].curriculum_message == "नम"
    assert message_objects[1].curriculum_message == "こん"
    assert message_objects[0].curriculum_index == 1
    assert message_objects[1].curriculum_index == 2
