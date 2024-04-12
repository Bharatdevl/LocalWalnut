from django.apps import AppConfig


class CompanyConfig(AppConfig):
    name = "company"
    verbose_name = "Companies"

    def ready(self):
        import company.signals
