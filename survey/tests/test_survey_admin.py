import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

from survey.admin import DefaultQuestion, DefaultQuestionAdmin


@pytest.fixture
def default_question_data():
    return {
        "question": "Test question",
        "created_at": "2022-01-01T12:00:00Z",
        "updated_at": "2022-01-02T12:00:00Z",
    }


def test_default_question_admin(admin_client, default_question_data):
    # Create a default question
    response = admin_client.post(
        "/admin/survey/defaultquestion/add/", default_question_data
    )

    assert response.status_code == 302

    # Check if the question is present in the list view
    response = admin_client.get("/admin/survey/defaultquestion/")
    assert "Test question" in str(response.content)
