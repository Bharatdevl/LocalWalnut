from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from twilio.base.exceptions import TwilioRestException

from services.twilio import twilio_sms_sender


@pytest.fixture
def mock_twilio_client(monkeypatch):
    mock_client = MagicMock()
    monkeypatch.setattr(
        "services.twilio.get_twilio_client", lambda: mock_client
    )
    return mock_client


def test_twilio_sms_sender_success(mock_twilio_client):
    phone_number = "1234567890"
    message = "Test message"

    with patch(
        "services.twilio.save_twilio_status"
    ) as mock_save_twilio_status:
        mock_save_twilio_status.return_value = True
        result = twilio_sms_sender(phone_number, message)
        assert result is True


# If not getting Twilio Client
def test_twilio_sms_sender_general_exception(mock_twilio_client):
    phone_number = "1234567890"
    message = "Test message"
    TWILIO_NUMBER = "000000"

    with patch(
        "services.twilio.save_twilio_status"
    ) as mock_save_twilio_status:
        mock_twilio_client.messages.create.side_effect = Exception(
            "fake exception"
        )
        mock_save_twilio_status.return_value = False

        result = twilio_sms_sender(phone_number, message)

        assert result is False


# If phone number or twilio Config is Invalid(AUTH_TOEKN, ACCOUNT_SID, TWILIO_NUMBER)
def test_twilio_sms_sender_invalid_twilio_credential(mock_twilio_client):
    phone_number = "1234567890"
    message = "Test message"
    TWILIO_NUMBER = "0000000"
    with patch(
        "services.twilio.save_twilio_status"
    ) as mock_save_twilio_status:
        mock_twilio_client.return_value = mock_twilio_client
        mock_twilio_client.messages.create.side_effect = TwilioRestException
        mock_save_twilio_status.return_value = False

        result = twilio_sms_sender(phone_number, message)

        assert result is False
