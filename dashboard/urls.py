from django.urls import path

from dashboard import views

# namespace app
app_name = "dashboard"


urlpatterns = [
    path("", views.home_view, name="home"),
    path("filter-data/", views.filter_data, name="filter_data"),
]
