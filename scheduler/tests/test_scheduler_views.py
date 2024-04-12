import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

from company.models import Company, CompanyUsers
from scheduler import utils, views
from scheduler.models import ScheduleCurriculum, ScheduleSurvey, WeekDays


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


def test_scheduler_survey_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:scheduler_survey"))
    assert response.status_code == 200
    assert "Survey" in str(response.content)


def test_scheduler_curriculum_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:scheduler_curriculum"))
    assert response.status_code == 200
    assert "Curriculum" in str(response.content)


def test_add_survey_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:add_survey"))
    assert response.status_code == 200
    assert "Survey" in str(response.content)


def test_check_weekday_list_render_survey_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:add_survey"))
    assert "Monday" in str(response.content)
    assert "Sunday" in str(response.content)


def test_check_schedule_time_list_render_survey_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:add_survey"))
    assert "8:00 AM" in str(response.content)
    assert "8:00 PM" in str(response.content)


def test_add_curriculum_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:add_curriculum"))
    assert response.status_code == 200
    assert "Curriculum" in str(response.content)


def test_check_weekday_list_render_survey_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:add_curriculum"))
    assert "Monday" in str(response.content)
    assert "Sunday" in str(response.content)


def test_check_schedule_time_list_render_curriculum_view(
    client, user_and_company
):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(reverse("scheduler:add_curriculum"))
    assert "8:00 AM" in str(response.content)
    assert "8:00 PM" in str(response.content)


def test_schedule_successfully_add_schedulesurvey_view(
    client, user_and_company
):
    user, company = user_and_company
    client.force_login(user)
    # Prepare POST data
    data = {
        "schedule_time": "12:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }
    response = client.post(reverse("scheduler:add_survey"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Survey scheduled successfully!" in messages

    schedule_survey = ScheduleSurvey.objects.first()
    assert schedule_survey.company.company_name == "abc company"


def test_schedule_survey_invalid_format_schedule_time(
    client, user_and_company
):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "12:00:00",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(reverse("scheduler:add_survey"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Invalid time format. Please use HH:MM AM/PM format."
        in messages
    )


def test_schedule_survey_invalid_schedule_time(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "9:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(reverse("scheduler:add_survey"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Schedule time should be between 8:00 AM and 8:00 PM."
        in messages
    )


def test_schedule_survey_invalid_weekday_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "12:00 PM",
        "weekday": "Invalid Day",
        "company": company,
    }

    response = client.post(reverse("scheduler:add_survey"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Message :Invalid weekday. Please select a valid day." in messages


def test_schedule_curriculum_successfully_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    # Prepare POST data
    data = {
        "schedule_time": "12:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(reverse("scheduler:add_curriculum"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Curriculum scheduled successfully!" in messages

    schedule_curriculum = ScheduleCurriculum.objects.first()
    assert schedule_curriculum.company.company_name == "abc company"


def test_curriculum_schedular_view_post_weekday(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)

    # Prepare POST data for weekdays
    data = {
        "schedule_time": "12:00 PM",
        "weekday": "weekdays",  # Set weekday to weekdays to trigger the loop
    }

    response = client.post(reverse("scheduler:add_curriculum"), data=data)

    assert response.status_code == 302  # Redirect status code

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Curriculum scheduled successfully for weekdays" in messages
    )  # Use the last message in the list

    # Check that five ScheduleCurriculum objects are created
    assert ScheduleCurriculum.objects.count() == 5

    # Additional assertions if needed
    for schedule_curriculum in ScheduleCurriculum.objects.all():
        assert schedule_curriculum.company.company_name == "abc company"
        assert (
            schedule_curriculum.schedule_time.strftime("%I:%M %p")
            == "12:00 PM"
        )


def test_schedule_curriculum_invalid_format_schedule_time(
    client, user_and_company
):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "12:00:00",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(reverse("scheduler:add_curriculum"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Invalid time format. Please use HH:MM AM/PM format."
        in messages
    )


def test_schedule_curriculum_invalid_schedule_time(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "9:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(reverse("scheduler:add_curriculum"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Schedule time should be between 8:00 AM and 8:00 PM."
        in messages
    )


def test_schedule_curriculum_invalid_weekday_view(client, user_and_company):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "12:00 PM",
        "weekday": "Invalid Day",
        "company": company,
    }

    response = client.post(reverse("scheduler:add_curriculum"), data=data)

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Message :Invalid weekday. Please select a valid day." in messages


# test cases for edit_survey_schedular


@pytest.fixture
def schedule_survey(db, user_and_company):
    user, company = user_and_company
    return ScheduleSurvey.objects.create(
        schedule_time="12:00:00",
        weekday=WeekDays.MONDAY,
        company=company,
    )


def test_get_edit_survey_schedular(client, user_and_company, schedule_survey):
    user, company = user_and_company
    client.force_login(user)
    response = client.get(
        reverse("scheduler:edit_survey", kwargs={"pk": schedule_survey.pk})
    )
    assert response.status_code == 200
    assert "Edit Schedule SMS" in str(response.content)


def test_post_edit_survey_schedular_successfully(
    client, user_and_company, schedule_survey
):
    user, company = user_and_company
    client.force_login(user)
    # Prepare POST data
    data = {
        "schedule_time": "2:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }
    response = client.post(
        reverse("scheduler:edit_survey", kwargs={"pk": schedule_survey.pk}),
        data=data,
    )

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Survey scheduled Update successfully!" in messages

    schedule_survey = ScheduleSurvey.objects.first()
    assert schedule_survey.company.company_name == "abc company"


def test_post_edit_survey_schedular_invalid_format_schedule_time(
    client, user_and_company, schedule_survey
):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "12:00:00",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(
        reverse("scheduler:edit_survey", kwargs={"pk": schedule_survey.pk}),
        data=data,
    )

    assert response.status_code == 200

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Invalid time format. Please use HH:MM AM/PM format."
        in messages
    )


def test_post_edit_survey_schedular_invalid_schedule_time(
    client, user_and_company, schedule_survey
):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "9:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(
        reverse("scheduler:edit_survey", kwargs={"pk": schedule_survey.pk}),
        data=data,
    )

    assert response.status_code == 200

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Schedule time should be between 8:00 AM and 8:00 PM."
        in messages
    )


def test_delete_schedule_survey(client, schedule_survey, user_and_company):
    user, company = user_and_company
    client.force_login(user)

    delete_url = reverse("scheduler:delete_survey", args=[schedule_survey.pk])

    response = client.delete(delete_url)

    assert response.status_code == 302
    assert response.url == reverse("scheduler:scheduler_survey")

    assert not ScheduleSurvey.objects.filter(pk=schedule_survey.pk).exists()
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Survey deleted successfully!" in messages

    assert response.url == reverse("scheduler:scheduler_survey")


# test cases for RUD with Curriculum Scheduler


@pytest.fixture
def curriculum_survey(db, user_and_company):
    user, company = user_and_company
    return ScheduleCurriculum.objects.create(
        schedule_time="12:00:00",
        weekday=WeekDays.MONDAY,
        company=company,
    )


def test_post_edit_curriculum_survey_successfully(
    client, user_and_company, curriculum_survey
):
    user, company = user_and_company
    client.force_login(user)
    # Prepare POST data
    data = {
        "schedule_time": "2:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }
    response = client.post(
        reverse(
            "scheduler:edit_curriculum", kwargs={"pk": curriculum_survey.pk}
        ),
        data=data,
    )

    assert response.status_code == 302

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Curriculum scheduled Update successfully!" in messages

    schedule_survey = ScheduleCurriculum.objects.first()
    assert schedule_survey.company.company_name == "abc company"


def test_post_edit_curriculum_survey_invalid_format_schedule_time(
    client, user_and_company, curriculum_survey
):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "12:00:00",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(
        reverse(
            "scheduler:edit_curriculum", kwargs={"pk": curriculum_survey.pk}
        ),
        data=data,
    )

    assert response.status_code == 200

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Invalid time format. Please use HH:MM AM/PM format."
        in messages
    )


def test_post_edit_curriculum_survey_invalid_schedule_time(
    client, user_and_company, curriculum_survey
):
    user, company = user_and_company
    client.force_login(user)
    data = {
        "schedule_time": "9:00 PM",
        "weekday": WeekDays.MONDAY,
        "company": company,
    }

    response = client.post(
        reverse(
            "scheduler:edit_curriculum", kwargs={"pk": curriculum_survey.pk}
        ),
        data=data,
    )

    assert response.status_code == 200

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert (
        "Message :Schedule time should be between 8:00 AM and 8:00 PM."
        in messages
    )


def test_delete_curriculum(client, curriculum_survey, user_and_company):
    user, company = user_and_company
    client.force_login(user)

    delete_url = reverse(
        "scheduler:delete_curriculum", args=[curriculum_survey.pk]
    )

    response = client.delete(delete_url)

    assert response.status_code == 302
    assert response.url == reverse("scheduler:scheduler_curriculum")

    assert not ScheduleCurriculum.objects.filter(
        pk=curriculum_survey.pk
    ).exists()
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "Curriculum deleted successfully!" in messages

    assert response.url == reverse("scheduler:scheduler_curriculum")
