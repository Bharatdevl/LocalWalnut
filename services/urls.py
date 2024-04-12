from django.urls import path

from services import views

# namespace app
app_name = "services"

urlpatterns = [
    path("sms/", views.inbound_sms, name="sms"),
    path("status/", views.sms_status, name="status"),
]
