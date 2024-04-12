import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.urls import reverse

from employee.models import Employee
from walnuteq.utils import required_login

from .forms import AddUserForm
from .models import Company, CompanyUsers


def login_company_users(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            u = CompanyUsers.objects.get(email=username)
            login_user = authenticate(username=username, password=password)
            if login_user is not None:
                login(request, login_user)
                return redirect(reverse("dashboard:home"), permanent=True)
            else:
                messages.error(
                    request, message="Invalid username and password"
                )
            return render(
                request, "company/login.html", {"title": "Company Login"}
            )
        except ObjectDoesNotExist:
            messages.error(request, message="Invalid username and password")
            return render(
                request, "company/login.html", {"title": "Company Login"}
            )
    return render(request, "company/login.html", {"title": "Company Login"})


@required_login
def logout_company_user(request):
    logout(request)
    messages.success(request, "Logout successful. Have a great day!")
    return redirect(reverse("company:company_users_login"), permanent=True)


@required_login
def add_user_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        phone_number = request.POST["phone_number"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password != confirm_password:
            messages.error(
                request, "Password and Confirm Password do not match."
            )
            return redirect("company:add_user")

        form = AddUserForm(request.POST)
        if form.is_valid():
            payload = form.cleaned_data
            logged_in_user = request.user
            company_user = CompanyUsers.objects.get(user=logged_in_user)
            company_id = company_user.company

            if Employee.objects.filter(email=email).exists():
                messages.error(
                    request,
                    "Email already exists . Please use a different one.",
                )
                return redirect("company:add_user")

            if Employee.objects.filter(phone_number=phone_number).exists():
                messages.error(
                    request,
                    "Phone number already exists . Please use a different one.",
                )
                return redirect("company:add_user")

            # Create a new user with the provided data
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(username=email)
                user.set_password(password)
                user.save()
            else:
                messages.error(request, "Email Already Exist .")
                return redirect("company:add_user")

            company_user = CompanyUsers(
                user=user,
                company=company_id,
                first_name=payload.get("first_name"),
                last_name=payload.get("last_name"),
                email=payload.get("email"),
                phone_number=payload.get("phone_number"),
                department=payload.get("department"),
                designation=payload.get("designation"),
                access_role="company_staff",
            )
            company_user.save()

            messages.success(request, "Client data saved successfully.")
            return render(request, "company/add-user.html")
        else:
            # Handle the case when the form is not valid
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Message :{error}")
            return render(request, "company/add-user.html")
    else:
        logged_in_user = request.user
        company_user = CompanyUsers.objects.get(user=logged_in_user)
        initial_data = {
            "company": company_user.company.company_name,
            "access_role": "company_staff",
        }
        form = AddUserForm(initial=initial_data)

    return render(
        request, "company/add-user.html", {"title": "Add Admin", "forms": form}
    )
