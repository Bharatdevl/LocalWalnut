from pathlib import Path

from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from company.models import Company
from walnuteq.settings import BASE_DIR

from .models import *


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ["id", "curriculum_name"]


@admin.register(Curriculum_Message)
class Curriculum_MessageAdmin(admin.ModelAdmin):
    """
    add a functionality search by curriculum_message and curriculum_index on admin side and also add a filter feature to filter a
    curriculum  all data with respect to that curriculum from admin panel.
    """

    list_display = ["curriculum", "curriculum_message", "curriculum_index"]
    # search_fields=("curriculum_message","curriculum_index")
    list_filter = ["curriculum"]


@admin.register(UploadCurriculumfile)
class UploadCurriculumfileAdmin(admin.ModelAdmin):
    list_display = ["id", "curriculum_name"]


@admin.register(CurriculumStack)
class CurriculumstackAdmin(admin.ModelAdmin):
    list_display = ["companies", "curriculum_list"]
    change_form_template = str(
        Path(BASE_DIR).joinpath("templates", "curriculum", "change_form.html")
    )

    def add_view(
        self, request: HttpRequest, form_url="", extra_context=None
    ) -> HttpResponse:
        if request.method == "POST":
            # Get the selected company from dropdown (admin panel )
            selected_company_id = request.POST.get(
                "companies"
            )  # Get the selected company ID
            selected_company = Company.objects.get(
                id=selected_company_id
            )  # Get the selected company from model

            # Check if a curriculum stack already exists for the selected company
            if CurriculumStack.objects.filter(
                companies=selected_company
            ).exists():
                error_message = (
                    "A curriculum stack already exists for this company."
                )
                messages.error(
                    request, error_message, extra_tags="error"
                )  # Set extra_tags to 'error' for red color
                return super().add_view(request, form_url, extra_context)

            # Get the inputs and curriculums from admin panel
            curriculum_inputs = {}
            for elm in Curriculum.objects.all():
                curriculum_input = request.POST.get(
                    elm.curriculum_name
                )  # Get the curriculum input
                curriculum_inputs[elm.curriculum_name] = curriculum_input

            # Sort curriculums according to the input numbers in textinput

            # Before sorting, filter out entries with None values
            curriculum_inputs_filtered = {
                curriculum: input_number
                for curriculum, input_number in curriculum_inputs.items()
                if input_number is not None
            }

            # Sort the curriculum inputs by the input number
            sorted_curriculums = sorted(
                curriculum_inputs_filtered.items(), key=lambda x: int(x[1])
            )
            # sorted_curriculums = sorted(curriculum_inputs.items(), key=lambda x: int(x[1]))  # Sort the curriculum inputs by the input number

            # Validate the curriculum inputs
            valid_curriculums = []
            num_curriculums = len(sorted_curriculums)
            error_messages = []
            used_indexes = set()
            for curriculum, input_number in sorted_curriculums:
                if not input_number.isdigit():
                    error_messages.append(f"Invalid input for {curriculum}")
                elif int(input_number) <= 0:
                    error_messages.append(
                        f"Input number should be greater than zero for {curriculum}"
                    )
                elif int(input_number) > num_curriculums:
                    error_messages.append(
                        f"Input number is out of range for {curriculum}"
                    )
                elif input_number in used_indexes:
                    error_messages.append(
                        f"Duplicate input number for {curriculum}"
                    )
                else:
                    valid_curriculums.append(curriculum)
                    used_indexes.add(input_number)

            # Render error messages to admin panel

            if error_messages:
                for error_message in error_messages:
                    messages.error(request, error_message, extra_tags="error")
                return super().add_view(request, form_url, extra_context)

            # Save the sorted curriculums and selected company in the Curriculum_Stack model
            curriculum_stack = CurriculumStack.objects.create(
                companies=selected_company
            )
            curriculum_list = ",".join(
                [curriculum for curriculum, _ in sorted_curriculums]
            )
            curriculum_stack.curriculum_list = curriculum_list

            # Save the curriculum inputs
            curriculum_inputs = ",".join(
                [
                    f"{curriculum}:{input_number}"
                    for curriculum, input_number in sorted_curriculums
                ]
            )
            curriculum_stack.curriculum_inputs = curriculum_inputs

            curriculum_stack.save()
            return redirect(
                reverse(
                    "admin:%s_%s_changelist"
                    % (self.model._meta.app_label, self.model._meta.model_name)
                )
            )

        return super().add_view(request, form_url, extra_context)

    def changeform_view(
        self, request, object_id=None, form_url="", extra_context=None
    ):
        extra_context = extra_context or {}
        # Render companies and curriculums to custom_change_form.html
        extra_context["companies"] = Company.objects.all()
        extra_context["curriculums"] = Curriculum.objects.all()

        if object_id:  # Editing an existing CurriculumStack object
            curriculum_stack = CurriculumStack.objects.get(pk=object_id)

            # Prepare the context to render the edit_curriculum_stack.html template
            extra_context["selected_company"] = curriculum_stack.companies

            if request.method == "POST":
                # Get the inputs and curriculums from admin panel
                curriculum_inputs = {}
                for elm in Curriculum.objects.all():
                    curriculum_input = request.POST.get(
                        elm.curriculum_name
                    )  # Get the curriculum input

                    curriculum_inputs[elm.curriculum_name] = curriculum_input

                # Sort curriculums according to the input numbers in textinput
                sorted_curriculums = sorted(
                    curriculum_inputs.items(),
                    key=lambda x: int(x[1])
                    if x[1] is not None
                    else float("inf"),
                )

                # Validate the curriculum inputs
                valid_curriculums = []
                num_curriculums = len(sorted_curriculums)
                error_messages = []
                used_indexes = set()
                for curriculum, input_number in sorted_curriculums:
                    if not input_number.isdigit():
                        error_messages.append(
                            f"Invalid input for {curriculum}"
                        )
                    elif int(input_number) <= 0:
                        error_messages.append(
                            f"Input number should be greater than zero for {curriculum}"
                        )
                    elif int(input_number) > num_curriculums:
                        error_messages.append(
                            f"Input number is out of range for {curriculum}"
                        )
                    elif input_number in used_indexes:
                        error_messages.append(
                            f"Duplicate input number for {curriculum}"
                        )
                    else:
                        valid_curriculums.append(curriculum)
                        used_indexes.add(input_number)

                # Render error messages to admin panel
                if error_messages:
                    for error_message in error_messages:
                        messages.error(
                            request, error_message, extra_tags="error"
                        )
                    return redirect(
                        reverse(
                            "admin:%s_%s_change"
                            % (
                                self.model._meta.app_label,
                                self.model._meta.model_name,
                            ),
                            args=[object_id],
                        )
                    )

                sorted_curriculums = sorted(
                    curriculum_inputs.items(), key=lambda x: int(x[1])
                )
                serialized_curriculum_inputs = ",".join(
                    [
                        f"{curriculum}:{input_number}"
                        for curriculum, input_number in sorted_curriculums
                    ]
                )

                # Update the current CurriculumStack object with the new curriculum inputs and curriculum_list
                curriculum_stack.curriculum_inputs = (
                    serialized_curriculum_inputs
                )
                curriculum_list = ",".join(
                    [curriculum for curriculum, _ in sorted_curriculums]
                )
                curriculum_stack.curriculum_list = curriculum_list
                curriculum_stack.save()  # Save the changes to the database
                messages.success(
                    request,
                    "Curriculum inputs have been updated successfully.",
                )

                return redirect(
                    reverse(
                        "admin:%s_%s_changelist"
                        % (
                            self.model._meta.app_label,
                            self.model._meta.model_name,
                        )
                    )
                )

            # Handle curriculum_inputs parsing and error handling
            curriculum_inputs = {}
            try:
                if curriculum_stack.curriculum_inputs:
                    input_pairs = curriculum_stack.curriculum_inputs.split(",")
                    for pair in input_pairs:
                        curriculum_name, input_number = pair.split(":")
                        curriculum_inputs[curriculum_name.strip()] = int(
                            input_number.strip()
                        )
            except (ValueError, AttributeError):
                # If curriculum_inputs is empty or not in the expected format, set curriculum_inputs to an empty dictionary
                curriculum_inputs = {}

            sorted_curriculums = sorted(
                curriculum_inputs.items(),
                key=lambda x: x[1] if x[1] is not None else float("inf"),
            )
            extra_context["curriculum_inputs"] = curriculum_inputs
            extra_context["sorted_curriculums"] = sorted_curriculums

            self.change_form_template = "curriculum/edit_curriculum_stack.html"
            return super().changeform_view(
                request, object_id, form_url, extra_context
            )

        # For adding a new CurriculumStack object, use the custom template
        if self.model == CurriculumStack:
            self.change_form_template = "curriculum/custom_change_form.html"

        return super().changeform_view(
            request, object_id, form_url, extra_context
        )
