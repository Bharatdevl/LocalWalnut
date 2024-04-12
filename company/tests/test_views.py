import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse

from company.models import Company, CompanyUsers
from company.views import add_user_view


@pytest.fixture
def user_login_data():
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    user = User.objects.create_user(
        username="john.doe@abc.com", password="pass123"
    )
    user.save()
    CompanyUsers(
        company=company_obj,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="0000000000",
        email="john.doe@abc.com",
        access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
    ).save()


def test_login_render_page(client):
    response = client.get(reverse("company:company_users_login"))
    assert response.status_code == 200
    assert "Company Login" in str(response.content)


def test_invalid_username_password(client):
    response = client.post(
        reverse("company:company_users_login"),
        {"username": "dummy", "password": "dummy"},
    )
    assert response.status_code == 200
    assert "invalid username and password" in str(response.content).lower()


def test_successful_login(client, user_login_data):
    response = client.post(
        reverse("company:company_users_login"),
        {"username": "john.doe@abc.com", "password": "pass123"},
    )
    assert response.status_code == 301
    assert response.url == reverse("dashboard:home")


def test_logout_company_users(client, user_login_data):
    response = client.post(
        reverse("company:company_users_login"),
        {"username": "john.doe@abc.com", "password": "pass123"},
    )
    response = client.get(reverse("company:company_users_logout"))
    assert response.status_code == 301
    assert response.url == reverse("company:company_users_login")


@pytest.mark.skip("login required is being temporarily bypassed..")
def test_login_required_for_dashboard_home(client):
    response = client.get(reverse("company:company_home"))
    assert response.status_code == 302
    assert response.url == "/company/login?next=/"


def test_add_user_view(client):
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    user = User.objects.create_user(
        username="john.doe@abc.com", password="pass123"
    )
    user.save()
    client.force_login(user)
    CompanyUsers(
        company=company_obj,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="0000000000",
        email="test@example.com",
        access_role=CompanyUsers.AccessRole.COMPANY_STAFF,
    ).save()

    post_data = {
        "email": "test@example.com",
        "phone_number": "1234567890",
        "password": "testpassword",
        "confirm_password": "testpassword",
        "first_name": "John",
        "last_name": "Doe",
        "designation": "Manager",
    }

    response = client.post(reverse("company:add_user"), post_data)

    assert CompanyUsers.objects.count() == 1
    assert CompanyUsers.objects.get(email="test@example.com")
