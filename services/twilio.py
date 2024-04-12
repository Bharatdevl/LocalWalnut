import datetime

from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from .models import TwilioStatus

ACCOUNT_SID = settings.ACCOUNT_SID
TWILIO_NUMBER = settings.TWILIO_NUMBER
AUTH_TOKEN = settings.AUTH_TOKEN
TWILIO_STATUS_CALLBACK_LINK = settings.TWILIO_STATUS_CALLBACK_LINK


def get_twilio_client():
    try:
        if not (TWILIO_NUMBER and ACCOUNT_SID and AUTH_TOKEN):
            raise Exception("Incomplete Twilio configuration in settings")

        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        return client

    except Exception as e:
        print("could not get config info from settings")
        return None


def twilio_sms_sender(phone_number, message):
    twilio_client = get_twilio_client()
    if not twilio_client:
        print("Error in getting the Twilio client")
        return False
    else:
        try:
            twilio_response = twilio_client.messages.create(
                to="+" + "1" + str(phone_number),
                from_=TWILIO_NUMBER,
                status_callback=TWILIO_STATUS_CALLBACK_LINK,
                body=message,
            )
            # Save TwilioStatus instance, ACCOUNT_SID
            return save_twilio_status(
                phone_number, TWILIO_NUMBER, twilio_response
            )
        except TwilioRestException as msg:
            # Handle Invalid Phone Number or TWILIO_NUMBER or ACCOUNT_SID or AUTH_TOKEN
            print(
                f"Invalid Phone Number or TWILIO_NUMBER or ACCOUNT_SID or AUTH_TOKEN"
            )
            error_code = "Invalid Phone_number or Twilio Credntial"
            return save_twilio_status(
                phone_number, TWILIO_NUMBER, None, error_code
            )
        except Exception as e:
            # Handle errors and log them
            print(f"Error sending SMS: {e}")
            error_code = "Some_Error"
            return save_twilio_status(
                phone_number, TWILIO_NUMBER, None, error_code
            )


def save_twilio_status(
    employee_phone_number, from_number, twilio_response=None, error_code=None
):
    # Create and save TwilioStatus instance
    if twilio_response and twilio_response.error_code:
        error_code = twilio_response.error_code
    twilio_status = TwilioStatus(
        sms_id=twilio_response.sid if twilio_response else None,
        status=twilio_response.status if twilio_response else "failed",
        employee_phone_number=str(employee_phone_number),
        from_number=str(from_number),
        error_code=error_code,
    )
    twilio_status.save()
    if error_code or twilio_response is None:
        return False
    return twilio_status
