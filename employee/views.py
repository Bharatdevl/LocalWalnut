import csv
import os
import re

import pandas as pd
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import validate_email
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from company.models import Company, CompanyUsers
from walnuteq.utils import required_login

from .forms import EmployeeForm
from .models import Employee


def paginate_data(request, data, items_per_page):
    paginator = Paginator(data, items_per_page)
    page = request.GET.get("page")

    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_data = paginator.page(1)
    except EmptyPage:
        paginated_data = paginator.page(paginator.num_pages)

    return paginated_data


@required_login
def employee_view(request):
    print("user", request.user)
    user = get_object_or_404(CompanyUsers, user=request.user)

    company_admin = CompanyUsers.objects.filter(
        company=user.company, access_role=CompanyUsers.AccessRole.COMPANY_ADMIN
    )
    company_staff = CompanyUsers.objects.filter(
        company=user.company, access_role=CompanyUsers.AccessRole.COMPANY_STAFF
    )

    emp_data = Employee.objects.filter(company=user.company)

    payload = request.GET
    if payload.get("search"):
        emp_data = emp_data.filter(
            Q(first_name__iexact=payload.get("search"))
            | Q(last_name__iexact=payload.get("search"))
            | Q(email__iexact=payload.get("search"))
            | Q(phone_number__iexact=payload.get("search"))
            | Q(location__iexact=payload.get("search"))
            | Q(department__iexact=payload.get("search"))
            | Q(job_title__iexact=payload.get("search"))
            | Q(supervisor__iexact=payload.get("search"))
        )
        company_admin = company_admin.filter(
            Q(first_name__iexact=payload.get("search"))
            | Q(last_name__iexact=payload.get("search"))
            | Q(email__iexact=payload.get("search"))
            | Q(phone_number__iexact=payload.get("search"))
        )

        company_staff = company_staff.filter(
            Q(first_name__iexact=payload.get("search"))
            | Q(last_name__iexact=payload.get("search"))
            | Q(email__iexact=payload.get("search"))
            | Q(phone_number__iexact=payload.get("search"))
        )

    show_all = request.GET.get("show_all")
    if show_all:
        return render(
            request,
            "employee/employee.html",
            {
                "emp_data": emp_data,
                "company_admin": company_admin,
                "company_staff": company_staff,
                "show_all": True,
            },
        )
    else:
        paginator = Paginator(emp_data, 5)
        page = request.GET.get("page")
        try:
            emp_data = paginator.page(page)
        except PageNotAnInteger:
            emp_data = paginator.page(1)
        except EmptyPage:
            emp_data = paginator.page(paginator.num_pages)

    return render(
        request,
        "employee/employee.html",
        {
            "company_admin": company_admin,
            "company_staff": company_staff,
            "emp_data": emp_data,
            "title": "Employee",
        },
    )


@required_login
def add_employee(request):
    user_email = request.user
    if request.method == "POST" and user_email:
        entity = CompanyUsers.objects.get(email=user_email)
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee_instance = form.save(commit=False)
            employee_instance.company = entity.company
            employee_instance.is_opted = True
            employee_instance.save()
            messages.success(request, "Employee data added successfully")
            return redirect("employee:employee_home")
        else:
            pass

    else:
        form = EmployeeForm()

    return render(
        request,
        "employee/add-employee.html",
        {"form": form, "title": "Employee"},
    )


def validate_file_extension(extension):
    return extension.lower() in [".csv", ".xlsx"]


def is_valid_email(email):
    # Use a regular expression for basic email validation
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return bool(re.match(email_regex, email))


def validate_columns(df, required_columns):
    file_columns = set(df.columns)
    if not required_columns.issubset(file_columns):
        raise ValidationError(
            "Required fields missing: {}".format(
                required_columns - file_columns
            )
        )


def validate_unique_fields(df, fields):
    duplicates = df.duplicated(fields).sum()
    if duplicates > 0:
        raise ValidationError("{} should be unique".format(", ".join(fields)))


def is_valid_name(name):
    if pd.notna(name) and isinstance(name, str):
        # Use a regular expression to check for valid names
        name_regex = re.compile(r"^[a-zA-Z]+$")
        return bool(re.match(name_regex, name))
    return False


def save_employee_data(df, company_user):
    df = df.drop_duplicates(
        ["phone_number", "email"], keep="last", ignore_index=True
    )
    invalid_emails = []
    duplicate_entries = []

    for _, row in df.iterrows():
        first_name = row.get("first_name", "")
        last_name = row.get("last_name", "")

        # Check if first_name and last_name are present and valid
        if (
            not first_name
            or not last_name
            or not is_valid_name(first_name)
            or not is_valid_name(last_name)
        ):
            raise ValidationError(
                "Please provide valid and non-empty first name and last name"
            )

        email = row.get("email")
        if not pd.notna(email) or not is_valid_email(email):
            invalid_emails.append(email)
            continue

        phone_number = row.get("phone_number")

        # Check if the email exists in CompanyUsers
        if CompanyUsers.objects.filter(email=email).exists():
            raise ValidationError(
                f"Email {email} already exists in CompanyUsers"
            )

        # Check if the phone number exists in CompanyUsers
        if CompanyUsers.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(
                f"Phone number {phone_number} already exists in CompanyUsers"
            )

        # Check if the email exists in Employee
        if Employee.objects.filter(email=email).exists():
            duplicate_entries.append({"email": email})

        # Check if the phone number exists in Employee
        if Employee.objects.filter(phone_number=phone_number).exists():
            duplicate_entries.append({"phone_number": phone_number})

    if invalid_emails:
        raise ValidationError(
            "Invalid email addresses : {}  add a valid email format ".format(
                ", ".join(invalid_emails)
            )
        )

    if duplicate_entries:
        raise ValidationError(
            "Email and Phone Number already Exist : {}".format(
                duplicate_entries
            )
        )

    Employee.objects.bulk_create(
        [
            Employee(
                first_name=row.get("first_name", "")
                if pd.notna(row.get("first_name"))
                else "",
                last_name=row.get("last_name", "")
                if pd.notna(row.get("last_name"))
                else "",
                middle_name=row.get("middle_name", "")
                if pd.notna(row.get("middle_name"))
                else "",
                email=row.get("email"),
                phone_number=row.get("phone_number"),
                job_title=row.get("job_title"),
                language=row.get("language"),
                department=row.get("department"),
                location=row.get("location"),
                supervisor=row.get("supervisor"),
                company=company_user.company,
            )
            for _, row in df.iterrows()
        ]
    )


@required_login
def upload_file(request):
    if request.method == "POST":
        try:
            file = request.FILES.get("file")
            user_email = request.user
            file_name, extension = os.path.splitext(str(file))

            if validate_file_extension(extension):
                df_group = (
                    pd.read_excel(file)
                    if extension == ".xlsx"
                    else pd.read_csv(file)
                )

                required_columns = {"email", "phone_number"}
                validate_columns(df_group, required_columns)

                unique_fields = ["email", "phone_number"]
                validate_unique_fields(df_group, unique_fields)

                company_user = CompanyUsers.objects.get(email=user_email)

                save_employee_data(df_group, company_user)

                messages.success(request, "Data saved successfully")
                return redirect("employee:employee_home")
            else:
                messages.error(request, "File format must be .csv or .xlsx")

        except ValidationError as ve:
            error_message = ve.messages[0] if ve.messages else str(ve)
            messages.error(request, error_message)

    return render(request, "employee/upload-data.html")


@required_login
def delete_employee(request, pk):
    """
    delete_emp function get a Emplloyee using pk and if employee present then delete
    it else raise an Exception
    """
    try:
        emp_data = Employee.objects.get(pk=pk)
        emp_data.delete()
        messages.success(request, "Employee details deleted")
        return redirect("employee:employee_home")
    except Exception as e:
        messages.error(request, f"Employee details falied to upate due to{e}")
        return render(request, "employee/employee.html")


@required_login
def download_all_employees_csv(request):
    """
    Download all employee data in CSV format
    """
    entity = CompanyUsers.objects.get(user=request.user)
    emp_data = Employee.objects.filter(company=entity.company)
    payload = request.GET

    if payload.get("search"):
        emp_data = emp_data.filter(
            Q(first_name__iexact=payload.get("search"))
            | Q(last_name__iexact=payload.get("search"))
            | Q(location__iexact=payload.get("search"))
            | Q(department__iexact=payload.get("search"))
            | Q(job_title__iexact=payload.get("search"))
            | Q(supervisor__iexact=payload.get("search"))
        )

    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="all_employees.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    # Write CSV header
    writer.writerow(
        [
            "First Name",
            "Last Name",
            "Email",
            "Phone Number",
            "Supervisor",
            "Department",
            "Location",
        ]
    )

    # Write employee data to CSV
    for employee in emp_data:
        writer.writerow(
            [
                employee.first_name,
                employee.last_name,
                employee.email,
                employee.phone_number,
                employee.supervisor,
                employee.department,
                employee.location,
            ]
        )

    return response


@required_login
def employee_Edit_view(request, pk):
    session_email = request.user
    try:
        entity = CompanyUsers.objects.get(email=session_email)
    except CompanyUsers.DoesNotExist:
        messages.error(
            request, "You are not authorized to edit this employee."
        )
        return redirect(
            "login"
        )  # Redirect to the login page or another relevant page

    try:
        emp_data = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return render(request, "employee/edit-employee.html")

    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=emp_data)
        if form.is_valid():
            form.instance.is_opted = emp_data.is_opted
            form.save()

            messages.success(request, "Employee details updated.")
            return redirect("employee:employee_home")
    else:
        form = EmployeeForm(instance=emp_data)

    return render(
        request,
        "employee/edit-employee.html",
        {"form": form, "emp_data": emp_data},
    )
