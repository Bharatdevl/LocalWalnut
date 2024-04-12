from django.urls import path

from survey import views

# namespace app
app_name = "survey"

urlpatterns = [
    path("", views.survey_view, name="survey_home"),
    path("add-question/", views.add_question_view, name="add_question"),
    path(
        "edit-question/<int:pk>/",
        views.edit_question_view,
        name="edit_question",
    ),
    path(
        "delete-question/<int:pk>/",
        views.delete_question_view,
        name="delete_question",
    ),
]
