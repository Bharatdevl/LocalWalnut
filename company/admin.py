from django.contrib import admin

from .forms import CompanyUsersForm
from .models import Company, CompanyUsers


# from surveyqa.models import DefaultQuestion,Question
# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["company_name", "created_at", "updated_at"]
    search_fields = ["company_name"]
    # def save_model(self, request, obj, form, change):
    #     super().save_model(request,obj,form,change)
    #     if obj.id and not change:
    #         if not Question.objects.filter(company_id=obj.id).exists():
    #             defaultquestion = DefaultQuestion.objects.all()
    #             for question in defaultquestion:
    #                 Question(name=question.name,company_id=obj.id).save()


@admin.register(CompanyUsers)
class CompanyUserAdmin(admin.ModelAdmin):
    form = CompanyUsersForm
    list_display = ["email", "phone_number", "company", "access_role"]
    list_filter = ["company", "access_role"]
    search_fields = ["email", "phone_number"]
