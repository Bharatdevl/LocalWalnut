from enum import Enum

from .twilio import twilio_sms_sender


# Service Proider (now we use twilio but we can also add some other service provider)
class ServiceProvider(Enum):
    twilio = "twilio"


# The function returns true if message sent is successful else false
def send_sms(phone_number, message, provider):
    if not message:
        "message not be Empty"
        return False
    elif provider == ServiceProvider.twilio:
        return twilio_sms_sender(phone_number, message)
    else:
        return False
