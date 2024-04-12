import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from company.models import Company
from conftest import admin_client
from curriculum.admin import *
from curriculum.models import Curriculum, Curriculum_Message, CurriculumStack


def test_curriculum_admin_list(admin_client):
    curriculum = Curriculum.objects.create(curriculum_name="Test Curriculum")

    response = admin_client.get("/admin/curriculum/curriculum/")
    assert response.status_code == 200

    assert curriculum.curriculum_name in str(response.content)


def test_curriculum_message_admin_list(admin_client):
    curriculum = Curriculum.objects.create(curriculum_name="Test Curriculum")

    curriculum_message = Curriculum_Message.objects.create(
        curriculum=curriculum,
        curriculum_message="Test Message",
        curriculum_index=1,
    )

    response = admin_client.get("/admin/curriculum/curriculum_message/")
    assert response.status_code == 200

    assert str(curriculum_message.curriculum_message) in str(response.content)


@pytest.fixture
def sample_company(db):
    return Company.objects.create(company_name="Test Company")


@pytest.fixture
def sample_curriculums(db):
    curriculum1 = Curriculum.objects.create(
        curriculum_name="Test Curriculum 1"
    )
    curriculum2 = Curriculum.objects.create(
        curriculum_name="Test Curriculum 2"
    )
    return curriculum1, curriculum2


@pytest.fixture
def curriculum_stack_data(sample_company, sample_curriculums):
    return {
        "companies": sample_company.id,
        f"curriculum_name_{sample_curriculums[0].id}": "1",
        f"curriculum_name_{sample_curriculums[1].id}": "2",
    }


def test_curriculum_admin_list(admin_client):
    response = admin_client.get(
        reverse("admin:curriculum_curriculum_changelist")
    )
    assert response.status_code == 200


def test_curriculum_message_admin_list(admin_client):
    curriculum = Curriculum.objects.create(curriculum_name="Test Curriculum")

    curriculum_message = Curriculum_Message.objects.create(
        curriculum=curriculum,
        curriculum_message="Test Message",
        curriculum_index=1,
    )

    response = admin_client.get(
        reverse("admin:curriculum_curriculum_message_changelist")
    )
    assert response.status_code == 200


def test_curriculum_stack_admin_add_view(
    admin_client, sample_company, sample_curriculums
):
    curriculum_stack_data = {
        "companies": sample_company.id,
        f"curriculum_name_{sample_curriculums[0].id}": "1",
        f"curriculum_name_{sample_curriculums[1].id}": "2",
    }

    response = admin_client.post(
        reverse("admin:curriculum_curriculumstack_add"), curriculum_stack_data
    )
    assert response.status_code == 302

    assert CurriculumStack.objects.filter(companies=sample_company).exists()
