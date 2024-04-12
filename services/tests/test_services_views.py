import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from twilio.twiml.messaging_response import MessagingResponse

from services.models import TwilioStatus
from services.views import inbound_sms


def test_inbound_sms_view(client):
    response = client.post(
        reverse("services:sms"),
        {
            "Body": "Test message",
            "From": "+1234567890",
            "To": "+0987654321",
            "SmsStatus": "received",
        },
    )
    assert response.status_code == 200
    assert "application/xml" in response.headers["Content-Type"]


@pytest.fixture
def rf():
    return RequestFactory()


def test_inbound_sms_post(rf):
    data = {
        "Body": "5",
        "From": "+1234567890",
        "To": "+9876543210",
        "SmsStatus": "received",
    }
    request = rf.post("services:sms", data)
    response = inbound_sms(request)
    assert response.status_code == 200


def test_inbound_sms_get(rf):
    request = rf.get("services:sms")
    response = inbound_sms(request)
    assert response.status_code == 405


def test_inbound_sms_invalid_rating(rf):
    data = {
        "Body": "abc",
        "From": "+1234567890",
        "To": "+9876543210",
        "SmsStatus": "received",
    }
    request = rf.post("services:sms", data)
    response = inbound_sms(request)
    assert response.status_code == 200
    assert "Please provide rating between 0 to 9" in response.content.decode()


def test_inbound_sms_rating_out_of_range(rf):
    data = {
        "Body": "10",
        "From": "+1234567890",
        "To": "+9876543210",
        "SmsStatus": "received",
    }
    request = rf.post("services:sms", data)
    response = inbound_sms(request)
    assert response.status_code == 200
    assert "Please provide rating between 0 to 9" in response.content.decode()


def test_inbound_sms_start_subscription(rf):
    data = {
        "Body": "start",
        "From": "+1234567890",
        "To": "+9876543210",
        "SmsStatus": "received",
    }
    request = rf.post("services:sms", data)
    response = inbound_sms(request)
    assert response.status_code == 200


@pytest.fixture
def twilio_status(db):
    return TwilioStatus.objects.create(sms_id="test_sid")


def test_sms_status_view(client, twilio_status):
    # Mock Twilio webhook notification
    webhook_data = {
        "SmsSid": "test_sid",
        "SmsStatus": "delivered",
        "To": "test_to",
        "From": "test_from",
        "ErrorCode": "",
    }

    response = client.post(reverse("services:status"), data=webhook_data)

    # Assert the response
    assert response.status_code == 200
    assert response.content == b"Twilio webhook processed successfully."

    # Refresh the twilio_status instance from the database
    twilio_status.refresh_from_db()
    # Assert the changes made by the view

    assert twilio_status.status == "delivered"
    assert twilio_status.error_code == None


def test_sms_status_view_does_not_exist(client):
    # Mock Twilio webhook notification for a non-existing SmsSid
    webhook_data = {
        "SmsSid": "non_existing_sid",
        "SmsStatus": "failed",
        "To": "test_to",
        "From": "test_from",
        "ErrorCode": "test_error",
    }

    response = client.post(reverse("services:status"), data=webhook_data)

    # Assert the response
    assert response.status_code == 200
    assert response.content == b"TwilioStatus not found for the given SmsSid."
