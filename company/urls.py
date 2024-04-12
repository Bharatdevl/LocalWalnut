from django.urls import path

from company import views

# namespace app
app_name = "company"

urlpatterns = [
    path("add-user/", views.add_user_view, name="add_user"),
    path("login/", views.login_company_users, name="company_users_login"),
    path(
        "logout",
        views.logout_company_user,
        name="company_users_logout",
    ),
]
