from celery import shared_task
from django.conf import settings
from django.utils import timezone

from company.models import CompanyUsers
from curriculum.models import Curriculum, Curriculum_Message, CurriculumStack
from employee import utils
from employee.models import Employee
from scheduler import models
from scheduler import utils as util
from services.send_sms import ServiceProvider, send_sms
from survey.models import Question

"""
Sends scheduled survey questions via Twilio SMS to opted employees, admins, and staff
for each company. Manages question counters and ScheduleStatus to ensure a continuous flow
of surveys during scheduled times.
"""


@shared_task
def send_survey_questions():
    tz = timezone.get_current_timezone()
    now_utc = timezone.now()
    now = timezone.localtime(now_utc, timezone=tz)
    current_weekday = now.strftime("%A").lower()
    current_hour = now.hour
    current_minute = now.minute
    company_list = []
    # Fetch all companies with scheduled surveys
    scheduled_surveys = models.ScheduleSurvey.objects.all()

    if scheduled_surveys:
        for survey in scheduled_surveys:
            if (
                current_weekday == survey.weekday
                and current_hour == survey.schedule_time.hour
                and current_minute == survey.schedule_time.minute
            ):
                company_list.append(survey.company)

        print("Company List for Current Schedule time", company_list)

        for company in company_list:
            # Fetch opted employees, admins, and staff for the company
            all_employees = Employee.objects.filter(
                company=company, is_opted=True
            )
            all_admins = CompanyUsers.objects.filter(
                company=company, access_role="company_admin", is_opted=True
            )
            all_staff = CompanyUsers.objects.filter(
                company=company, access_role="company_staff", is_opted=True
            )

            all_recipients = (
                list(all_employees) + list(all_admins) + list(all_staff)
            )

            # Fetch all survey questions for the company
            all_questions = Question.objects.filter(company=company).order_by(
                "created_at"
            )
            print("All Employee", all_recipients)
            print("All Question", all_questions)

            # Fetch or create ScheduleStatus for the company
            (
                schedule_status,
                created,
            ) = models.ScheduleStatus.objects.get_or_create(company=company)

            if created:
                print("Created new ScheduleStatus for company:", company)

            for recipient in all_recipients:
                # Get the current question index from the counter
                scheduled_count = schedule_status.question_schedule_counter

                # Check if all questions have been sent
                if scheduled_count >= len(all_questions):
                    # Reset the counter when reaching the end of the question list
                    scheduled_count = 0
                    schedule_status.question_schedule_counter = scheduled_count
                    schedule_status.save()

                question_content = all_questions[scheduled_count]
                print("Question content:", question_content.question)

                # Twilio trigger to send the SMS survey question
                result = send_sms(
                    recipient.phone_number,
                    question_content.question,
                    ServiceProvider.twilio,
                )
                if result:
                    utils.create_employee_rating(
                        company=company,
                        employee_phone_number=recipient.phone_number,
                        question=question_content,
                        sms_id=result.sms_id,
                        status=result.status,
                        send_timestamp=now,
                        expire_timestamp=now,
                    )
                    # Call the function for calculate a average rating
                    average_rating = utils.calculate_question_average_rating(
                        question_content, company
                    )
                    question_content.last_avg_rating = average_rating
                    question_content.send_timestamp = now  #  Update the send_timestamp field of the Question object
                    question_content.save()

            # Increment the counter for the next question
            schedule_status.question_schedule_counter += 1
            schedule_status.save()

        return f"current_weekday:{current_weekday}, -- current_hour_minute :{current_hour,current_minute}"
    else:
        print("There is No Scheduler for the current day:", current_weekday)

    return f"current_weekday:{current_weekday}, -- current_hour_minute :{current_hour,current_minute}, No schedule for the day"


"""
Sends scheduled curriculum messages via Twilio SMS to opted employees, admins, and staff
for each company. Manages curriculum counters and status to ensure a continuous flow
of curriculum messages during scheduled times.
"""


@shared_task
def send_curriculum_schedule():
    # Get the current time information
    tz = timezone.get_current_timezone()
    now_utc = timezone.now()
    now = timezone.localtime(now_utc, timezone=tz)
    current_weekday = now.strftime("%A").lower()
    current_hour = now.hour
    current_minute = now.minute
    company_list = []
    # Fetch all companies with scheduled curriculums
    scheduled_curriculums = models.ScheduleCurriculum.objects.all()

    for curriculum_schedule in scheduled_curriculums:
        # Check if the current time matches the scheduled time for curriculum
        if (
            current_weekday == curriculum_schedule.weekday
            and current_hour == curriculum_schedule.schedule_time.hour
            and current_minute == curriculum_schedule.schedule_time.minute
        ):
            company_list.append(curriculum_schedule.company)

    print("Company List for Current Curriculum Schedule time", company_list)

    redis_connection = settings.REDIS_CURRICULUM_CONN
    if redis_connection:
        if company_list:
            for company in company_list:
                print("Curriculum company", company)
                try:
                    # Fetch the curriculum stack for the company
                    curriculum_stack = CurriculumStack.objects.get(
                        companies=company
                    )
                    curriculum_list = curriculum_stack.curriculum_list.split(
                        ","
                    )
                except Exception as e:
                    print(
                        f"There is no Curriculum stack for {company} company"
                    )
                    continue
                if curriculum_list:
                    # Fetch opted employees, admins, and staff for the company
                    all_employees = Employee.objects.filter(
                        company=company, is_opted=True
                    )
                    all_admins = CompanyUsers.objects.filter(
                        company=company,
                        access_role="company_admin",
                        is_opted=True,
                    )
                    all_staff = CompanyUsers.objects.filter(
                        company=company,
                        access_role="company_staff",
                        is_opted=True,
                    )

                    all_recipients = (
                        list(all_employees)
                        + list(all_admins)
                        + list(all_staff)
                    )

                    for recipient in all_recipients:
                        is_queue_empty = util.is_queue_empty(recipient)
                        if is_queue_empty:
                            util.store_messages_in_redis(
                                recipient, curriculum_list
                            )

                        message = util.retrieve_message_from_redis(recipient)
                        if message:
                            result = send_sms(
                                recipient.phone_number,
                                message,
                                ServiceProvider.twilio,
                            )
                        else:
                            print(
                                f"There is no curriculum message for this curriculum stack."
                            )
                else:
                    print(
                        f"There is no curriculum stack for {company} company."
                    )
        else:
            print(
                f"There is No Scheduler for the current day:{current_weekday} and current_hour_minute: {current_hour, current_minute}"
            )
            return f"There is No Scheduler for the current day:{current_weekday} and current_hour_minute: {current_hour, current_minute}"
    else:
        print("Redis connection is not established properly")
