from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Case, IntegerField, Value, When
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render

from company.models import CompanyUsers
from scheduler import utils
from scheduler.forms import ScheduleCurriculumForm, ScheduleSurveyForm
from scheduler.models import ScheduleCurriculum, ScheduleSurvey
from walnuteq.utils import required_login


@required_login
def scheduler_survey_view(request):
    # Access CompanyUsers Object
    user_obj_exists = CompanyUsers.objects.filter(email=request.user).exists()

    if user_obj_exists:
        company_obj = CompanyUsers.objects.get(email=request.user).company
        print("Client:", request.user, "Company:", company_obj)

        # Define a dictionary for weekday ordering
        weekday_ordering = utils.generate_weekday_ordering()

        # Annotate the ScheduleSurvey queryset with a custom_order field based on weekday_ordering
        schedule_surveys = (
            ScheduleSurvey.objects.filter(
                company=company_obj
            )  # Filter by user's company
            .annotate(
                custom_order=Case(
                    *[
                        When(weekday=weekday, then=Value(order))
                        for weekday, order in weekday_ordering.items()
                    ],
                    default=Value(7),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "schedule_time")
        )
        # Retrieve search parameters from the request
        search_weekday = request.GET.get("weekday", "")

        # Apply filters based on search parameters
        if search_weekday:
            schedule_surveys = schedule_surveys.filter(
                weekday__istartswith=search_weekday
            )

        items_per_page = 8
        paginator = Paginator(schedule_surveys, items_per_page)
        page = request.GET.get("page", 1)
        show_all = request.GET.get("show_all", False)

        if show_all == "true":
            schedule_obj = schedule_surveys
        else:
            try:
                schedule_obj = paginator.page(page)
            except PageNotAnInteger:
                schedule_obj = paginator.page(1)
            except EmptyPage:
                schedule_obj = paginator.page(paginator.num_pages)

        template_name = "scheduler/scheduler_survey.html"
        context = {
            "title": "Survey",
            "schedule_obj": schedule_obj,
            "show_all": show_all,
            "search_weekday": search_weekday,
        }
        return render(request, template_name, context)
    else:
        print("This Client Not Belong to any company:", request.user)
        return redirect("company:company_users_login")


@required_login
def scheduler_curriculum_view(request):
    # Access CompanyUsers Object
    user_obj_exists = CompanyUsers.objects.filter(email=request.user).exists()

    if user_obj_exists:
        company_obj = CompanyUsers.objects.get(email=request.user).company
        print("Client:", request.user, "Company:", company_obj)

        # Define a dictionary for weekday ordering
        weekday_ordering = utils.generate_weekday_ordering()

        # Do the same for ScheduleCurriculum
        schedule_curriculum = (
            ScheduleCurriculum.objects.filter(
                company=company_obj
            )  # Filter by user's company
            .annotate(
                custom_order=Case(
                    *[
                        When(weekday=weekday, then=Value(order))
                        for weekday, order in weekday_ordering.items()
                    ],
                    default=Value(7),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "schedule_time")
        )
        # Retrieve search parameters from the request
        search_weekday = request.GET.get("weekday", "")

        # Apply filters based on search parameters
        if search_weekday:
            schedule_curriculum = schedule_curriculum.filter(
                weekday__istartswith=search_weekday
            )

        items_per_page = 8
        paginator = Paginator(schedule_curriculum, items_per_page)
        page = request.GET.get("page", 1)
        show_all = request.GET.get("show_all", False)

        if show_all == "true":
            schedule_obj = schedule_curriculum
        else:
            try:
                schedule_obj = paginator.page(page)
            except PageNotAnInteger:
                schedule_obj = paginator.page(1)
            except EmptyPage:
                schedule_obj = paginator.page(paginator.num_pages)

        template_name = "scheduler/scheduler_curriculum.html"
        context = {
            "title": "Curriculum",
            "schedule_obj": schedule_obj,
            "show_all": show_all,
            "search_weekday": search_weekday,
        }

        return render(request, template_name, context)
    else:
        print("This Client Not Belong to any company:", request.user)
        return redirect("company:company_users_login")


@required_login
def survey_schedular_view(request):
    if request.method == "GET":
        return render(
            request,
            "scheduler/add-schedule.html",
            {
                "title": "Survey",
                "schedular_type": "survey",
                "weekdays": utils.get_weekday_list(),
                "schedule_time_list": utils.get_schedule_time_list(),
            },
        )
    elif request.method == "POST":
        payload = request.POST

        """We need to update the QueryDict as it now includes additional company object."""

        query_dict = QueryDict("", mutable=True)
        query_dict.update(payload)

        # Access CompanyUsers Object
        user_obj_exists = CompanyUsers.objects.filter(
            email=request.user
        ).exists()

        if user_obj_exists:
            company_obj = CompanyUsers.objects.get(email=request.user).company
            print("Client:", request.user)
        else:
            print("This Client Not Belong to any company:", request.user)
            company_obj = None

        # Update the QueryDict instance with company_obj
        query_dict.setlist("company", [company_obj])
        # Create the ScheduleSurveyForm object
        form = ScheduleSurveyForm(query_dict)
        if form.is_valid():
            form.save()
            messages.success(request, "Survey scheduled successfully!")
            return redirect("scheduler:add_survey")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Message :{error}")
            return redirect("scheduler:add_survey")


@required_login
def edit_survey_schedular(request, pk):
    schedule_survey = get_object_or_404(ScheduleSurvey, pk=pk)
    referrer_url = request.META.get("HTTP_REFERER", "")  # getting url
    if request.method == "GET":
        return render(
            request,
            "edit-schedule-sms.html",
            {
                "schedule_obj": schedule_survey,
                "referrer_url": referrer_url,
            },
        )
    elif request.method == "POST":
        payload = request.POST
        """We need to update the QueryDict as it now includes additional company object."""
        query_dict = QueryDict("", mutable=True)
        query_dict.update(payload)

        # Access CompanyUsers Object
        user_obj_exists = CompanyUsers.objects.filter(
            email=request.user
        ).exists()

        if user_obj_exists:
            company_obj = CompanyUsers.objects.get(email=request.user).company
            print("Client:", request.user)
        else:
            print("This Client Not Belong to any company:", request.user)
            company_obj = None

        # Update the QueryDict instance with company_obj
        query_dict.setlist("company", [company_obj])
        form = ScheduleSurveyForm(query_dict, instance=schedule_survey)
        referrer_url = request.POST.get("referrer_url", "")
        if form.is_valid():
            form.save()
            messages.success(request, "Survey scheduled Update successfully!")
            if referrer_url:
                return redirect(referrer_url)
            else:
                return redirect("scheduler:scheduler_survey")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Message :{error}")
            return render(
                request,
                "edit-schedule-sms.html",
                {
                    "schedule_obj": schedule_survey,
                    "referrer_url": referrer_url,
                },
            )


@required_login
def delete_survey_schedular(request, pk):
    referrer_url = request.META.get("HTTP_REFERER", "")  # getting url
    try:
        schedule_survey = get_object_or_404(ScheduleSurvey, pk=pk)
        schedule_survey.delete()
        referrer_url = request.GET.get("referrer", referrer_url)
        messages.success(request, "Survey deleted successfully!")

    except ScheduleSurvey.DoesNotExist:
        messages.error(request, "Survey not found.")
    if referrer_url:
        return redirect(referrer_url)
    else:
        return redirect("scheduler:scheduler_survey")


@required_login
def curriculum_schedular_view(request):
    if request.method == "GET":
        return render(
            request,
            "scheduler/add-schedule.html",
            {
                "title": "Curriculum",
                "schedular_type": "curriculum",
                "weekdays": utils.get_weekday_list_curriculum(),
                "schedule_time_list": utils.get_schedule_time_list(),
            },
        )
    elif request.method == "POST":
        payload = request.POST
        query_dict = QueryDict("", mutable=True)
        query_dict.update(payload)

        # Access CompanyUsers Object
        user_obj_exists = CompanyUsers.objects.filter(
            email=request.user
        ).exists()

        if user_obj_exists:
            company_obj = CompanyUsers.objects.get(email=request.user).company
            print("Client:", request.user)
        else:
            print("This Client Not Belong to any company:", request.user)
            company_obj = None

        """We need to update the QueryDict as it now includes additional company object."""
        query_dict.setlist("company", [company_obj])
        weekday = payload.get("weekday")
        if weekday == "weekdays":
            count = 0
            weekdays = utils.get_weekdays()
            for weekday in weekdays:
                query_dict.setlist("weekday", [weekday])
                form = ScheduleCurriculumForm(query_dict)
                if form.is_valid():
                    form.save()
                else:
                    count += 1
            if count == 5:
                messages.error(
                    request,
                    "Curriculum scheduled with this Schedule time and Weekdays already exists.",
                )
                return redirect("scheduler:add_curriculum")
            else:
                messages.success(
                    request, "Curriculum scheduled successfully for weekdays"
                )
                return redirect("scheduler:add_curriculum")

        # Create the ScheduleCurriculumForm object
        form = ScheduleCurriculumForm(query_dict)

        if form.is_valid():
            form.save()
            messages.success(request, "Curriculum scheduled successfully!")
            return redirect("scheduler:add_curriculum")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Message :{error}")
            return redirect("scheduler:add_curriculum")


@required_login
def edit_curriculum_schedular(request, pk):
    schedule_curriculum = get_object_or_404(ScheduleCurriculum, pk=pk)
    referrer_url = request.META.get("HTTP_REFERER", "")  # getting url
    if request.method == "GET":
        return render(
            request,
            "edit-schedule-curriculum.html",
            {
                "schedule_obj": schedule_curriculum,
                "referrer_url": referrer_url,
            },
        )
    elif request.method == "POST":
        payload = request.POST
        """We need to update the QueryDict as it now includes additional company object."""
        query_dict = QueryDict("", mutable=True)
        query_dict.update(payload)
        #
        # Access CompanyUsers Object
        user_obj_exists = CompanyUsers.objects.filter(
            email=request.user
        ).exists()
        #
        if user_obj_exists:
            company_obj = CompanyUsers.objects.get(email=request.user).company
            print("Client:", request.user)
        else:
            print("This Client Not Belong to any company:", request.user)
            company_obj = None
        #
        # Update the QueryDict instance with company_obj
        query_dict.setlist("company", [company_obj])
        referrer_url = request.POST.get("referrer_url", "")
        form = ScheduleCurriculumForm(query_dict, instance=schedule_curriculum)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Curriculum scheduled Update successfully!"
            )
            if referrer_url:
                return redirect(referrer_url)
            else:
                return redirect("scheduler:scheduler_curriculum")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Message :{error}")
            return render(
                request,
                "edit-schedule-sms.html",
                {
                    "schedule_obj": schedule_curriculum,
                    "referrer_url": referrer_url,
                },
            )


@required_login
def delete_curriculum_schedular(request, pk):
    referrer_url = request.META.get("HTTP_REFERER", "")  # getting url
    try:
        schedule_curriculum = get_object_or_404(ScheduleCurriculum, pk=pk)
        schedule_curriculum.delete()
        referrer_url = request.GET.get("referrer", referrer_url)
        messages.success(request, "Curriculum deleted successfully!")
    except ScheduleCurriculum.DoesNotExist:
        messages.error(request, "Curriculum not found.")
    if referrer_url:
        return redirect(referrer_url)
    else:
        return redirect("scheduler:scheduler_curriculum")
