from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from employee.models import Employee

from .models import CompanyUsers
from .utils import generate_random_password, send_mail_with_attachment


class CompanyUsersForm(forms.ModelForm):
    class Meta:
        model = CompanyUsers
        exclude = ["user"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")

        if email and Employee.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        if (
            phone_number
            and Employee.objects.filter(phone_number=phone_number).exists()
        ):
            raise forms.ValidationError("Phone number already exists .")

    def save(self, commit=True):
        usrname = self.cleaned_data.get("email")
        password = generate_random_password(6)
        access_role = self.cleaned_data.get("access_role")
        print("access_role", access_role)
        if not User.objects.filter(username=usrname).exists():
            user = User.objects.create_user(username=usrname)
            user.set_password(password)
            user.save()
            """Pass the User instance to the password_sendmail function
            """
            self.instance.user = user
            self.instance.password = password
            if access_role == "company_staff":
                pass
            else:
                send_mail_with_attachment(self.instance, password)
        return super().save(commit)


class AddUserForm(forms.ModelForm):
    # company = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CompanyUsers
        exclude = ["user", "access_role", "company"]

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        if not first_name.isalpha():
            raise forms.ValidationError(
                "Only characters are allowed in the first name."
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        if not last_name.isalpha():
            raise forms.ValidationError(
                "Only characters are allowed in the last name."
            )
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")

        if email and User.objects.filter(email=email).exists():
            self.add_error(
                "email", "Email already exists. Please use a different one."
            )

        if (
            phone_number
            and CompanyUsers.objects.filter(phone_number=phone_number).exists()
        ):
            self.add_error(
                "phone_number",
                "Phone number already exists. Please use a different one.",
            )

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CompanyUsers.objects.filter(email=email).exists():
            raise ValidationError(
                "Email already exists. Please use a different one."
            )

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if CompanyUsers.objects.filter(phone_number=phone).exists():
            raise ValidationError(
                "Phone number already exists. Please use a different one."
            )

        return phone

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if len(str(phone)) < 10:
            raise ValidationError(
                "Phone number should have a minimum of 10 digits."
            )

        return phone
