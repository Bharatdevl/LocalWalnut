from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.messaging_response import MessagingResponse

from company.models import CompanyUsers
from employee.models import Employee, EmployeeRating
from services.models import TwilioStatus


@require_POST
@csrf_exempt
def inbound_sms(request):
    response = MessagingResponse()
    if request.method == "POST":
        body = request.POST.get("Body", "").strip().lower()
        from_number = request.POST.get("From", "")
        to_number = request.POST.get("To", "")
        status = request.POST.get("SmsStatus", "")

        # Check if the string starts with "+1"
        if from_number.startswith("+1"):
            # Remove the "+1" prefix
            cleaned_from_number = from_number[2:]
        else:
            # No "+1" prefix, use the original number
            cleaned_from_number = from_number

        try:
            """
            if rating is not between range 0-9 then raise an error  'Please provide rating between 0 to 9'
            """
            if not body.isdigit():
                if body in ["start", "stop", "unstop"]:
                    try:
                        employee = Employee.objects.get(
                            phone_number=cleaned_from_number
                        )
                        if (
                            body == "start" or body == "unstop"
                        ) and employee.is_opted:
                            response.message(
                                "You have already subscribed. Reply STOP to unsubscribe."
                            )
                            return HttpResponse(
                                response, content_type="application/xml"
                            )
                        employee.is_opted = body == "start" or body == "unstop"
                        employee.save()
                        response.message("")
                        return HttpResponse(
                            response, content_type="application/xml"
                        )

                    except Employee.DoesNotExist:
                        # If Employee not found, try to find a CompanyUser
                        try:
                            company_user = CompanyUsers.objects.get(
                                phone_number=cleaned_from_number
                            )
                            if (
                                body == "start" or body == "unstop"
                            ) and company_user.is_opted:
                                response.message(
                                    "You have already subscribed. Reply STOP to unsubscribe."
                                )
                                return HttpResponse(
                                    response, content_type="application/xml"
                                )
                            company_user.is_opted = (
                                body == "start" or body == "unstop"
                            )
                            company_user.save()
                            response.message("")
                            return HttpResponse(
                                response, content_type="application/xml"
                            )

                        except CompanyUsers.DoesNotExist:
                            response.message("something went wrong")
                            return HttpResponse(
                                response, content_type="application/xml"
                            )
                elif body == "help":
                    response.message("")
                    return HttpResponse(
                        response, content_type="application/xml"
                    )

                else:
                    body = "Please provide rating between 0 to 9"
                    response.message(body)
                    return HttpResponse(
                        response, content_type="application/xml"
                    )

            # if rating len is greater than 1 then raise an error  'Please provide rating between 0 to 9'
            elif len(body) > 1:
                body = "Please provide rating between 0 to 9"
                response.message(body)
                return HttpResponse(response, content_type="application/xml")
            else:
                try:
                    # Access the last EmployeeRating object for the employee
                    last_employee_rating = EmployeeRating.objects.filter(
                        employee_phone_number=cleaned_from_number,
                        status__in=[
                            "accepted",
                            "queued",
                            "received",
                            "delivered",
                            "responded",
                        ],
                    ).last()
                    if last_employee_rating:
                        # Update the rating attribute based on the body content
                        last_employee_rating.rating = int(body)
                        last_employee_rating.status = "responded"
                        last_employee_rating.save()
                        body = ""
                    else:
                        print(
                            "EmployeeRating not found for the given phone number."
                        )
                        body = "something went wrong"
                except Exception as e:
                    print(f"Error in database call: {e}")
                    body = "something went wrong"
                response.message(body)
                return HttpResponse(response, content_type="application/xml")

        except Exception as e:
            body = "something went wrong"
            response.message(body)
            return HttpResponse(response, content_type="application/xml")
    else:
        # If it's not a POST request, return a 405 Method Not Allowed
        return HttpResponse(status=405)


@require_POST
@csrf_exempt
def sms_status(request):
    """
    sms_status handles Twilio webhook notifications for SMS status.
    When survey questions are sent to each employee, Twilio sends notifications
    for SMS status updates. This view processes those notifications and updates
    the TwilioStatus model accordingly.
    """
    try:
        # Extract information from Twilio webhook notification
        sid = request.POST.get("SmsSid")
        status = request.POST.get("SmsStatus", "")
        to = request.POST.get("To")
        from_number = request.POST.get("From")
        error_code = request.POST.get("ErrorCode", "")
        if status.lower() in ["failed", "undelivered"]:
            if EmployeeRating.objects.filter(sms_id=sid).exists():
                # Update the status of the EmployeeRating with the given sid
                employee_rating = EmployeeRating.objects.get(sms_id=sid)
                employee_rating.status = status
                employee_rating.save()
            # Update TwilioStatus based on sms_id
            twilio_status = TwilioStatus.objects.get(sms_id=sid)
            twilio_status.status = status
            twilio_status.error_code = error_code
            twilio_status.save()

        elif status.lower() in [
            "sent",
            "receiving",
            "accepted",
            "queued",
            "sending",
            "received",
            "delivered",
        ]:
            if EmployeeRating.objects.filter(sms_id=sid).exists():
                # Update the status of the EmployeeRating with the given sid
                employee_rating = EmployeeRating.objects.get(sms_id=sid)
                employee_rating.status = "delivered"
                employee_rating.save()
            # Update TwilioStatus based on sms_id
            twilio_status = TwilioStatus.objects.get(sms_id=sid)
            twilio_status.status = "delivered"
            twilio_status.save()

        print("Twilio webhook processed successfully.")
        return HttpResponse("Twilio webhook processed successfully.")

    except TwilioStatus.DoesNotExist:
        print("TwilioStatus not found for the given SmsSid.")
        return HttpResponse("TwilioStatus not found for the given SmsSid.")

    except Exception as e:
        print(str(e))  # Log the exception (consider using a logging library)
        return HttpResponse("Error processing Twilio webhook.")
