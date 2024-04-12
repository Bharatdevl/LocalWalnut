import pytest

from employee.forms import EmployeeForm
from employee.models import Employee


@pytest.fixture
def valid_employee_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        # Add other required fields as needed
    }


@pytest.fixture
def create_employee(valid_employee_data):
    return Employee.objects.create(**valid_employee_data)


@pytest.mark.django_db
def test_valid_employee_form(valid_employee_data):
    form = EmployeeForm(data=valid_employee_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_invalid_email_employee_form(valid_employee_data):
    valid_employee_data["email"] = "invalidemail"
    form = EmployeeForm(data=valid_employee_data)
    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.django_db
def test_duplicate_email_employee_form(valid_employee_data, create_employee):
    valid_employee_data["email"] = create_employee.email
    form = EmployeeForm(data=valid_employee_data, instance=create_employee)
    assert form.is_valid()


@pytest.mark.django_db
def test_duplicate_phone_number_employee_form(
    valid_employee_data, create_employee
):
    valid_employee_data["phone_number"] = str(create_employee.phone_number)
    form = EmployeeForm(data=valid_employee_data, instance=create_employee)
    assert form.is_valid()
