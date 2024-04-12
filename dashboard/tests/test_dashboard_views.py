import json
from math import ceil

import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse

from company.models import Company, CompanyUsers
from dashboard.views import filter_data
from employee.models import Employee, EmployeeRating
from survey.models import Question


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


@pytest.fixture
def question(user_and_company):
    user, company = user_and_company
    question_text = "How satisfied are you with your work?"
    return Question.objects.create(company=company, question=question_text)


@pytest.fixture
def employee_ratings(user_and_company, question):
    user, company = user_and_company
    ratings = []

    for i in range(5):
        rating = EmployeeRating.objects.create(
            company=company,
            question=question,
            rating=i + 1,
            status="responded",
        )
        ratings.append(rating)

    return ratings


@pytest.mark.django_db
def test_filter_data_weekly(
    client, user_and_company, question, employee_ratings
):
    user, company = user_and_company

    factory = RequestFactory()
    url = reverse("dashboard:filter_data")
    request = factory.get(url, {"month_id": 3})
    request.user = user

    response = filter_data(request)
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert "table_data" in data


@pytest.mark.django_db
def test_filter_data_monthly(user_and_company, question, employee_ratings):
    user, company = user_and_company

    factory = RequestFactory()
    url = reverse("dashboard:filter_data")
    request = factory.get(url, {"month_id": 6})
    request.user = user

    response = filter_data(request)
    data = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 200
    assert len(data["line_chart_data"]) > 0
    assert "table_data" in data
