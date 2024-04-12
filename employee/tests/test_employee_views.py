import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory
from django.urls import reverse

from company.models import Company, CompanyUsers
from employee.models import Employee
from employee.views import download_all_employees_csv, employee_view


def test_employee_view(client):
    company = Company.objects.create(company_name="Test Company")
    user = User.objects.create_user(
        username="testuser", email="testuser@example.com", password="password"
    )
    company_user = CompanyUsers.objects.create(
        company=company,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="1234567890",
        email="john.doe@example.com",
        access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
    )
    employee = Employee.objects.create(
        first_name="Jane",
        last_name="Doe",
        phone_number="9876543210",
        email="jane.doe@example.com",
        company=company,
    )

    request = RequestFactory().get("/employee/")
    request.user = user

    response = employee_view(request)

    assert response.status_code == 200

    assert str(employee.email) in response.content.decode("utf-8")
    assert str(employee.phone_number) in response.content.decode("utf-8")
    assert str(employee.first_name) in response.content.decode("utf-8")


@pytest.fixture
def user_and_company(db):
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
    return user, company_obj


@pytest.mark.django_db
def test_add_employee_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)

    response = client.post(
        reverse("employee:add_emp"),
        data={
            "first_name": "Test",
            "last_name": "Employee",
            "email": "test.employee@example.com",
            "phone_number": "9876543210",
            "department": "Test Department",
            "job_title": "Test Job Title",
            "location": "Test Location",
            "language": "Test Language",
            "supervisor": "Test Supervisor",
            "is_opted": True,
        },
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_upload_file(client, user_and_company):
    user, company_user = user_and_company
    client.force_login(user)

    file_content = "email,phone_number\njohn.doe@example.com,1234567890"
    file = SimpleUploadedFile("test_file.csv", file_content.encode())

    response = client.post(reverse("employee:file_data"), {"file": file})

    assert response.status_code == 200


@pytest.fixture
def user_company_and_employee(db):
    company = Company.objects.create(company_name="Test Company")
    user = User.objects.create_user(username="testuser", password="password")
    company_user = CompanyUsers.objects.create(
        company=company,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="1234567890",
        email="john.doe@test.com",
        access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
    )
    employee = Employee.objects.create(
        first_name="Test",
        last_name="Employee",
        email="test.employee@test.com",
        phone_number="9876543210",
        company=company,
    )
    return user, company, company_user, employee


@pytest.mark.django_db
def test_delete_employee_view(client, user_company_and_employee):
    user, company, company_user, employee = user_company_and_employee
    client.force_login(user)

    response = client.post(
        reverse("employee:delete_employee", args=[employee.pk])
    )

    assert response.status_code == 302

    with pytest.raises(Employee.DoesNotExist):
        Employee.objects.get(pk=employee.pk)

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Employee details deleted" in messages


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def user_company_and_employee(db):
    company = Company.objects.create(company_name="Test Company")
    user = User.objects.create_user(username="testuser", password="password")
    company_user = CompanyUsers.objects.create(
        company=company,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="1234567890",
        email="john.doe@test.com",
        access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
    )
    employee = Employee.objects.create(
        first_name="Test",
        last_name="Employee",
        email="test.employee@test.com",
        phone_number="9876543210",
        company=company,
    )
    return user, company, company_user, employee


@pytest.mark.django_db
def test_download_all_employees_csv(
    user_company_and_employee, request_factory
):
    user, company, company_user, employee = user_company_and_employee
    request = request_factory.get("/path/to/download")
    request.user = user

    response = download_all_employees_csv(request)

    assert response.status_code == 200

    assert response["Content-Type"] == "text/csv"

    expected_header = [
        "First Name",
        "Last Name",
        "Email",
        "Phone Number",
        "Supervisor",
        "Department",
        "Location",
    ]
    assert (
        response.content.decode().splitlines()[0].split(",") == expected_header
    )
    expected_data = [
        employee.first_name,
        employee.last_name,
        employee.email,
        str(employee.phone_number),
        employee.supervisor,
        employee.department,
        employee.location,
    ]

    expected_output_data = [
        "" if value is None else value for value in expected_data
    ]

    assert expected_output_data == response.content.decode().splitlines()[
        1
    ].split(",")


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.mark.django_db
def test_employee_edit_view(client):
    # Create a user
    user = User.objects.create_user(
        username="john.doe@abc.com", password="pass123"
    )

    # Create a company
    company = Company(company_name="abc company")
    company.save()

    # Create a CompanyUsers object
    company_user = CompanyUsers(
        company=company,
        user=user,
        first_name="John",
        last_name="Doe",
        phone_number="0000000000",
        email="john.doe@abc.com",
        access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
    )
    company_user.save()

    # Create an employee
    employee = Employee(
        first_name="Test",
        last_name="Employee",
        email="test.employee@example.com",
        phone_number="9876543210",
        department="Test Department",
        job_title="Test Job Title",
        location="Test Location",
        language="Test Language",
        supervisor="Test Supervisor",
        is_opted=True,
        company=company,
    )
    employee.save()

    # Log in the user
    client.force_login(user)

    # Make a GET request to the employee edit view
    response = client.get(
        reverse("employee:edit_employee", kwargs={"pk": employee.pk})
    )
    assert response.status_code == 200

    # Simulate a POST request with updated data
    response = client.post(
        reverse("employee:edit_employee", kwargs={"pk": employee.pk}),
        data={
            "first_name": "Updated",
            "last_name": "Employee",
            "email": "test.employee@example.com",
            "phone_number": "9876543210",
            "department": "Test Department",
            "job_title": "Test Job Title",
            "location": "Test Location",
            "language": "Test Language",
            "supervisor": "Test Supervisor",
            "is_opted": True,
        },
    )

    assert response.status_code == 200
