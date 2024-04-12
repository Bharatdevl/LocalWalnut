import os
from pathlib import Path
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

from company.models import Company, CompanyUsers
from company.tests.test_views import user_login_data
from company.utils import generate_random_password, send_mail_with_attachment

logo_folder = "static/images"
logo_file_name = "walnuteq_logo.png"
logo_file_path = os.path.join(settings.BASE_DIR, logo_folder, logo_file_name)


def test_generate_random_password():
    assert len(generate_random_password(6)) == 6
    assert generate_random_password(6).isalnum()


@pytest.fixture
def company_instance():
    return Company.objects.create(company_name="Test Company")


@pytest.fixture
def company_user_instance(company_instance):
    user = User.objects.create_user(
        username="john.doe@example.com", password="testpassword"
    )
    return CompanyUsers.objects.create(
        company=company_instance,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="1234567890",
        email="john.doe@example.com",
        access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
    )


@pytest.fixture
def instance_mock(user_login_data):
    user = CompanyUsers.objects.latest("id")

    return user


@pytest.fixture
def password_mock():
    return "test_password"


def test_send_mail_with_attachment(instance_mock, password_mock):
    os.environ["EMAIL_HOST_USER"] = "support@walnuteq.com"
    os.environ["LOGIN_URL"] = "https://yourloginurl.com"
    logo_file_path = "path/to/logo.png"

    # Call the function with mocked parameters
    result = send_mail_with_attachment(instance_mock, password_mock)
    assert result is True
