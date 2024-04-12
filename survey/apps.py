from django.apps import AppConfig


class SurveyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "survey"

    def ready(self):
        """
        This method is called when the Django application is being initialized.
        It imports the signals module to ensure that the signals are connected.
        """
        import survey.signals
