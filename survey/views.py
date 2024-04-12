from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render

from company.models import CompanyUsers
from survey.forms import QuestionForm
from survey.models import Question
from walnuteq.utils import required_login


@required_login
def survey_view(request):
    # Check if the user belongs to any company
    user_obj_exists = CompanyUsers.objects.filter(email=request.user).exists()

    if user_obj_exists:
        user_company = CompanyUsers.objects.get(email=request.user).company
        # User belongs to a company, proceed with rendering the survey
        questions = Question.objects.filter(company=user_company).order_by(
            "id"
        )
        return render(
            request,
            "survey/survey.html",
            {"title": "Survey", "question_obj": questions},
        )
    else:
        print("This Client Not Belong to any company:", request.user)
        return redirect("company:company_users_login")


@required_login
def add_question_view(request):
    if request.method == "GET":
        return render(
            request, "survey/add-question.html", {"title": "Add Question"}
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

        # Create the QuestionForm object
        form = QuestionForm(query_dict)
        if form.is_valid():
            form.save()
            messages.success(request, "Survey question added successfully!")
            return redirect("survey:add_question")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                if errors:
                    # Display only the first error message
                    first_error = errors[0]
                    messages.error(request, f"Message: {first_error}")

            # Pass the original question text back to the template
            original_question = payload.get("question", "")

            return render(
                request,
                "survey/add-question.html",
                {
                    "original_question": original_question,
                },
            )


@required_login
def edit_question_view(request, pk):
    # Get the existing question object or return a 404 response if not found
    question = get_object_or_404(Question, id=pk)

    if request.method == "GET":
        # Populate the form with the existing question data
        return render(
            request,
            "edit-survey.html",
            {"question_obj": question},
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

        # Create the QuestionForm object
        form = QuestionForm(query_dict, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Survey question updated successfully!")
            return redirect("survey:survey_home")
        else:
            # Display form errors
            for field, errors in form.errors.items():
                if errors:
                    # Display only the first error message
                    first_error = errors[0]
                    messages.error(request, f"Message: {first_error}")

            # Pass the original question text back to the template

            return render(
                request,
                "edit-survey.html",
                {
                    "question_obj": question,
                },
            )


@required_login
def delete_question_view(request, pk):
    try:
        # Get the existing question object or return a 404 response if not found
        question = get_object_or_404(Question, id=pk)
        question.delete()
        messages.success(request, "Survey question deleted successfully!")
    except Question.DoesNotExist:
        messages.error(request, "Question not found.")

    return redirect("survey:survey_home")
