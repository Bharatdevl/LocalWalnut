import pytest
from django.db import connection

from company.models import Company
from employee.models import Employee, EmployeeRating
from survey.models import Question


@pytest.fixture
def employee_data():
    company_obj = Company(company_name="abc company").save()
    Employee(
        first_name="John",
        last_name="Doe",
        phone_number="1234567890",
        email="John@doe.com",
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


def test_no_of_fields_company():
    # keep in mind id field is autogenerated so it also counts
    assert len(Employee._meta.fields) == get_number_of_fields(
        "employee_employee"
    )


def test_empty_list_of_employees():
    assert Employee.objects.all().count() == 0


def test_create_an_employee(employee_data):
    assert Employee.objects.all().count() == 1


@pytest.fixture
def employee_rating_data():
    company_obj = Company.objects.create(company_name="xyz company")
    question_obj = Question.objects.create(
        question="How are you?", company=company_obj
    )
    employee_rating_obj = EmployeeRating.objects.create(
        company=company_obj,
        employee_phone_number="123456789",
        question=question_obj,
        status="delivered",
        rating=8,
    )


def test_no_of_fields_employee_ratings():
    assert len(EmployeeRating._meta.fields) == get_number_of_fields(
        "employee_employeerating"
    )


def test_empty_list_of_employee_ratings():
    assert EmployeeRating.objects.all().count() == 0


def test_create_an_employee_ratings(employee_rating_data):
    assert EmployeeRating.objects.all().count() == 1
    assert (
        EmployeeRating.objects.latest("id").company.company_name
        == "xyz company"
    )


def test_employee_uuid_uniqueness():
    # Create a set to store generated UUIDs
    uuid_set = set()
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    # Create 10 employee objects and add their UUIDs to the set
    for i in range(10):
        employee = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="123456789"
            + str(i),  # Unique phone number for each employee
            email="john.doe{}@example.com".format(
                i
            ),  # Unique email for each employee
            company=company_obj
            # Add other required fields here
        )
        uuid_set.add(employee.employee_queue_key)

    # Assert that the number of UUIDs stored in the set is equal to the number of objects created
    assert len(uuid_set) == 10, "Each UUID should be unique"