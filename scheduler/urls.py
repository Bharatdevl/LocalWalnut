from django.urls import path

from scheduler import views

# namespace app
app_name = "scheduler"

urlpatterns = [
    path(
        "scheduler-survey",
        views.scheduler_survey_view,
        name="scheduler_survey",
    ),
    path(
        "scheduler-curriculum",
        views.scheduler_curriculum_view,
        name="scheduler_curriculum",
    ),
    path("add-survey/", views.survey_schedular_view, name="add_survey"),
    path(
        "edit-survey/<int:pk>/",
        views.edit_survey_schedular,
        name="edit_survey",
    ),
    path(
        "delete-survey/<int:pk>/",
        views.delete_survey_schedular,
        name="delete_survey",
    ),
    path(
        "add-curriculum/",
        views.curriculum_schedular_view,
        name="add_curriculum",
    ),
    path(
        "edit-curriculum/<int:pk>/",
        views.edit_curriculum_schedular,
        name="edit_curriculum",
    ),
    path(
        "delete-curriculum/<int:pk>/",
        views.delete_curriculum_schedular,
        name="delete_curriculum",
    ),
]
