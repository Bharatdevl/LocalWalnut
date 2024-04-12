import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

from company.models import Company, CompanyUsers
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


def test_survey_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("survey:survey_home"))
    assert response.status_code == 200
    assert "Survey" in str(response.content)


def test_add_question_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("survey:add_question"))
    assert response.status_code == 200
    assert "Add Question" in str(response.content)


def test_add_question_view_post_valid(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)

    data = {"question": "How are you?", "company": company}
    response = client.post(reverse("survey:add_question"), data)
    messages = [m.message for m in get_messages(response.wsgi_request)]

    assert response.status_code == 302
    assert "Survey question added successfully!" in messages
    assert Question.objects.filter(
        question="How are you?", company=company
    ).exists()


@pytest.fixture
def survey_question(db, user_and_company):
    user, company = user_and_company
    return Question.objects.create(question="How are you?", company=company)


def test_edit_question_view_get(client, user_and_company, survey_question):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(
        reverse("survey:edit_question", kwargs={"pk": survey_question.pk})
    )
    assert response.status_code == 200
    assert "Edit Questions" in str(response.content)


def test_edit_question_view_post_successfully(
    client, user_and_company, survey_question
):
    user, company = user_and_company
    client.force_login(user)
    # Prepare POST data
    data = {
        "question": "How many hours of sleep do you typically get each night"
    }
    response = client.post(
        reverse("survey:edit_question", kwargs={"pk": survey_question.pk}),
        data=data,
    )

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Survey question updated successfully!" in messages

    survey_question = Question.objects.first()
    assert (
        survey_question.question
        == "How many hours of sleep do you typically get each night"
    )


def test_delete_question_successfully(
    client, user_and_company, survey_question
):
    user, company = user_and_company
    client.force_login(user)
    url = reverse("survey:delete_question", args=[survey_question.id])

    response = client.delete(url)

    assert response.status_code == 302
    assert Question.objects.count() == 0
    assert response.url == reverse("survey:survey_home")
