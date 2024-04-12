import uuid

import pytest
from django.contrib.auth.models import User

from company.models import Company, CompanyUsers


@pytest.fixture
def company_admin_user_data():
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    return {
        "company": company_obj.id,
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "0000000000",
        "email": "john.doe@abc.com",
        "access_role": CompanyUsers.AccessRole.COMPANY_ADMIN,
        "employee_queue_key": uuid.uuid4(),
    }


def test_get_company_dashboard_load_status(admin_client):
    response = admin_client.get("/admin/company/company/")
    assert response.status_code == 200
    assert "Select Company to change | Django site admin" in str(
        response.content
    )


def test_create_company(admin_client):
    response = admin_client.post(
        "/admin/company/company/add/",
        {"company_name": "abc company", "_save": "Save"},
    )
    assert response.status_code == 302
    assert Company.objects.get(company_name="abc company")


def test_unique_company_validation(admin_client):
    Company(company_name="abc company").save()
    response = admin_client.post(
        "/admin/company/company/add/",
        {"company_name": "abc company", "_save": "Save"},
    )
    assert response.status_code == 200
    assert "Company with this Company name already exists" in str(
        response.content
    )


def test_get_companyuser_dashboard_load_status(admin_client):
    response = admin_client.get("/admin/company/companyusers/")
    assert response.status_code == 200
    assert "Select Company Users to change | Django site admin" in str(
        response.content
    )


def test_create_companyuser(admin_client, company_admin_user_data):
    response = admin_client.post(
        "/admin/company/companyusers/add/", company_admin_user_data
    )
    assert response.status_code == 302
    assert CompanyUsers.objects.get(email=company_admin_user_data.get("email"))


def test_create_companyuser_with_username_and_password(
    admin_client, company_admin_user_data
):
    _ = admin_client.post(
        "/admin/company/companyusers/add/", company_admin_user_data
    )
    assert User.objects.get(username=company_admin_user_data.get("email"))


def test_companyusers_phone_number_validation(
    admin_client, company_admin_user_data
):
    company_admin_user_data["phone_number"] = "1234567890"
    response = admin_client.post(
        "/admin/company/companyusers/add/", company_admin_user_data
    )
    assert response.status_code == 302
    assert CompanyUsers.objects.filter(
        email=company_admin_user_data["email"]
    ).exists()


def test_new_user_is_not_added_during_change(
    admin_client, company_admin_user_data
):
    _ = admin_client.post(
        "/admin/company/companyusers/add/", company_admin_user_data
    )

    company_obj = CompanyUsers.objects.latest("id")
    response = admin_client.post(
        f"/admin/company/companyusers/{company_obj.pk}/change/",
        company_admin_user_data,
    )

    assert response.status_code == 302
    assert User.objects.filter(username=company_obj.email).count() == 1
