import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, connection

from company.models import Company
from survey.models import DefaultQuestion, Question, UploadQAfile


@pytest.fixture
def question_data():
    company = Company.objects.create(company_name="abc company")
    question_obj = Question.objects.create(
        question="sample question",
        company=company,
        send_timestamp="2024-01-01T12:00:00",
        last_avg_rating=4.5,
    )
    return question_obj


def get_number_of_fields(model_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name = %s",
            (model_name,),
        )
        num_fields = cursor.fetchone()[0]
    return num_fields


def test_no_of_fields_surveyquestion():
    assert len(Question._meta.fields) == 7
    assert get_number_of_fields("survey_question") == 7


def test_surveyquestion_list_empty():
    assert Question.objects.count() == 0


def test_create_a_surveyquestion(question_data):
    assert Question.objects.count() == 1
    assert Question.objects.latest("id").question == "sample question"


def test_check_company_obj(question_data):
    surveyquestion_obj = Question.objects.latest("id")
    assert surveyquestion_obj.company.company_name == "abc company"


def test_unique_survey_question_obj(question_data):
    # Try to create another SurveyQestion with the same combination
    with pytest.raises(IntegrityError):
        company_obj = Company.objects.latest("id")
        Question.objects.create(
            question="sample question",
            company=company_obj,
            send_timestamp="2024-01-01T12:00:00",
            last_avg_rating=5.0,
        )


@pytest.fixture
def default_question_data():
    question_obj = DefaultQuestion.objects.create(
        question="How would you describe your current overall health",
    )
    return question_obj


def test_no_of_fields_defaultquestion():
    assert len(DefaultQuestion._meta.fields) == 4
    assert get_number_of_fields("survey_defaultquestion") == 4


def test_defaultquestion_list_empty():
    assert DefaultQuestion.objects.count() == 0


def test_create_a_default_question(default_question_data):
    assert DefaultQuestion.objects.count() == 1
    assert (
        DefaultQuestion.objects.latest("id").question
        == "How would you describe your current overall health"
    )


def test_upload_qa_file():
    # Create a sample company
    company = Company.objects.create(
        company_name="Test Company", description="Test Description"
    )

    # Create a sample CSV file with some questions
    csv_content = "Questions\nQuestion 01\nQuestion 02"
    csv_file = SimpleUploadedFile(
        "test_file_1.csv", csv_content.encode(), content_type="text/csv"
    )

    # Instantiate an UploadQAfile object
    upload_file = UploadQAfile(file_name=csv_file)

    # Call the clean method to process the file
    upload_file.clean()

    # Check if questions have been saved to the database
    assert DefaultQuestion.objects.filter(question="Question 01").count() == 1
    assert DefaultQuestion.objects.filter(question="Question 02").count() == 1

    # Check if questions have been assigned to the company
    # Get the count of questions assigned to the company
    assigned_questions_count = Question.objects.filter(company=company).count()

    # Get the count of questions created from the file
    created_questions_count = DefaultQuestion.objects.count()

    # Ensure the counts match
    assert assigned_questions_count == created_questions_count
