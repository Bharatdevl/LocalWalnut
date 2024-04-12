import pytest
from django.db.models.signals import post_delete, post_save

from company.models import Company
from survey import signals
from survey.models import DefaultQuestion, Question


@pytest.fixture
def default_question_data():
    return {"question": "Test Default Question"}


@pytest.fixture
def company_data():
    return {"company_name": "Test Company"}


@pytest.fixture
def setup_test_data(default_question_data, company_data):
    # Create DefaultQuestion and Company objects
    default_question = DefaultQuestion.objects.create(**default_question_data)
    company = Company.objects.create(**company_data)

    # Connect signals for the test
    post_save.connect(
        signals.copy_default_questions_to_companies, sender=DefaultQuestion
    )
    post_save.connect(
        signals.copy_default_questions_to_new_company, sender=Company
    )

    yield {"default_question": default_question, "company": company}

    # Disconnect signals and clean up after the test
    post_save.disconnect(
        signals.copy_default_questions_to_companies, sender=DefaultQuestion
    )
    post_save.disconnect(
        signals.copy_default_questions_to_new_company, sender=Company
    )

    default_question.delete()
    company.delete()


def test_copy_default_questions_to_companies_signal(setup_test_data):
    data = setup_test_data

    # Trigger the signal by saving a default question
    DefaultQuestion.objects.create(question="Another default question")

    # Check if the corresponding questions were created for all companies
    companies = Company.objects.all()
    for company in companies:
        question = Question.objects.get(
            question="Another default question", company=company
        )
        assert question is not None


def test_copy_default_questions_to_new_company_signal(setup_test_data):
    data = setup_test_data

    # Trigger the signal by saving a company
    Company.objects.create(company_name="Another Test Company")

    # Check if the questions from default questions were copied to the new company
    new_company = Company.objects.get(company_name="Another Test Company")
    default_question = DefaultQuestion.objects.first()
    question = Question.objects.get(
        question=default_question.question, company=new_company
    )
    assert question is not None
