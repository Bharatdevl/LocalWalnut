from django.urls import path
from django.views.generic import TemplateView

from employee import views

# namespace app
app_name = "employee"

urlpatterns = [
    path("", views.employee_view, name="employee_home"),
    path(
        "upload_files/",
        TemplateView.as_view(template_name="employee/upload-data.html"),
        name="upload_files",
    ),
    path("add_emp/", views.add_employee, name="add_emp"),
    path("file_data/", views.upload_file, name="file_data"),
    path(
        "download_all_employees_csv/",
        views.download_all_employees_csv,
        name="download_all_employees_csv",
    ),
    path(
        "delete_employee/<pk>", views.delete_employee, name="delete_employee"
    ),
    path("edit_employee/<pk>", views.employee_Edit_view, name="edit_employee"),
]
