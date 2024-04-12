import pytest

from services.send_sms import ServiceProvider, send_sms


@pytest.mark.skip(" We Have to Pass Real Number.")
def test_send_sms_suessfully():
    result = send_sms(
        "Actual Phone Number", "Test message", ServiceProvider.twilio
    )
    assert result is True


def test_send_sms_invalid_provider():
    result = send_sms("123", "Test message", "Invalid Provider")
    assert result is False


def test_send_sms_empty_message():
    result = send_sms("+123456789", "", ServiceProvider.twilio)
    assert result is False
