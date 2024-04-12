from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from company.models import CompanyUsers

from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "phone_number",
            "email",
            "department",
            "job_title",
            "location",
            "language",
            "supervisor",
            "is_opted",
        ]

    def clean(self):
        cleaned_data = super().clean()
        required_errors_shown = False

        for field_name, field in self.fields.items():
            value = cleaned_data.get(field_name)

            if (
                field.required
                and field_name in self.errors
                and not required_errors_shown
            ):
                required_errors_shown = True
                error_list = self.errors[field_name]
                error_message = error_list[0]  # Only display the first error

                # Add a custom error to the form
                self.add_error(None, f"{field.label} - {error_message}")

        return cleaned_data

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        if not first_name.isalpha():
            raise forms.ValidationError(
                "First name should contain only alphabetical characters."
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        if not last_name.isalpha():
            raise forms.ValidationError(
                "Last name should contain only alphabetical characters."
            )
        return last_name

    def clean_email(self):
        email = self.cleaned_data["email"]
        if (
            Employee.objects.filter(email=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "Email already exists. Please use a different one."
            )

        if CompanyUsers.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Email already exists in Company Users. Please use a different one."
            )

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email address.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if (
            Employee.objects.filter(phone_number=phone_number)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "Phone number already exists. Please use a different one."
            )

        if CompanyUsers.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "Phone number already exists. Please use a different one."
            )

        # Adding validation for minimum 10 digits
        if len(str(phone_number)) < 10:
            raise forms.ValidationError(
                "Phone number should have a minimum of 10 digits."
            )
        return phone_number

    def clean_department(self):
        department = self.cleaned_data["department"]
        if department is not None and not department.isalpha():
            raise forms.ValidationError(
                "Department should contain only alphabetical characters."
            )
        return department

    def clean_location(self):
        location = self.cleaned_data["location"]
        if location is not None and not location.isalpha():
            raise forms.ValidationError(
                "Location should contain only alphabetical characters."
            )
        return location

    def clean_supervisor(self):
        supervisor = self.cleaned_data["supervisor"]
        if supervisor is not None and not supervisor.isalpha():
            raise forms.ValidationError(
                "Supervisor should contain only alphabetical characters."
            )
        return supervisor
