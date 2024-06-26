import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.utils import IntegrityError

from company.models import Company, CompanyUsers
from company.utils import generate_random_password


@pytest.fixture
def company_user_data():
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    user = User.objects.create_user(
        username="john.doe@abc.com", password=generate_random_password(6)
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
    assert len(Company._meta.fields) == 5
    assert get_number_of_fields("company_company") == 5


def test_company_list_empty():
    assert Company.objects.count() == 0


def test_create_a_company():
    Company(company_name="abc company").save()
    assert Company.objects.count() == 1
    assert Company.objects.latest("id").company_name == "abc company"


def test_check_unique_company_name():
    Company(company_name="abc company").save()
    with pytest.raises(IntegrityError):
        Company(company_name="abc company").save()


def test_no_of_fields_company_users():
    assert len(CompanyUsers._meta.fields) == 16
    assert get_number_of_fields("company_companyusers") == 16


def test_company_user_list_empty():
    assert CompanyUsers.objects.count() == 0


def test_create_company_user(company_user_data):
    assert CompanyUsers.objects.count() == 1
    assert CompanyUsers.objects.get(email="john.doe@abc.com")


def test_unique_company_user(company_user_data):
    with pytest.raises(IntegrityError):
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


def test_check_no_alphabet_validation_phone_number(company_user_data):
    company_user_obj = CompanyUsers.objects.latest("id")
    with pytest.raises(ValidationError):
        company_user_obj.phone_number = "abc1234s"
        company_user_obj.full_clean()
        company_user_obj.save()


def test_check_access_role(company_user_data):
    company_obj = CompanyUsers.objects.latest("id")
    company_obj.access_role = CompanyUsers.AccessRole.COMPANY_ADMIN
    company_obj.save()
    assert company_obj.access_role == CompanyUsers.AccessRole.COMPANY_ADMIN


def test_companyuser_uuid_uniqueness():
    # Create a set to store generated UUIDs
    uuid_set = set()
    Company(company_name="abc company").save()
    company_obj = Company.objects.latest("id")
    # Create 10 employee objects and add their UUIDs to the set
    for i in range(10):
        user = User.objects.create_user(
            username="john.doe{}@example.com".format(i), password="pass123"
        )
        user.save()
        employee = CompanyUsers.objects.create(
            company=company_obj,
            user=user,
            first_name="John",
            last_name="Doe",
            phone_number="123456789" + str(i),
            email="john.doe{}@example.com".format(i),
            access_role=CompanyUsers.AccessRole.COMPANY_ADMIN,
            # Add other required fields here
        )
        uuid_set.add(employee.employee_queue_key)

    # Assert that the number of UUIDs stored in the set is equal to the number of objects created
    assert len(uuid_set) == 10, "Each UUID should be unique"
