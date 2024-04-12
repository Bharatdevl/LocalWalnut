from django.contrib import admin

from .models import DefaultQuestion, Question, UploadQAfile


@admin.register(DefaultQuestion)
class DefaultQuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the DefaultQuestion model.
    """

    list_display = ["question", "created_at", "updated_at"]
    search_fields = ["question"]


class UploadAQfileAdmin(admin.ModelAdmin):
    list_display = ["upload_on"]

    def upload_on(self, obj):
        if obj:
            try:
                if obj.upload_on:
                    return obj.upload_on
                else:
                    return None
            except:
                return obj.upload_on


class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "question",
        "company",
        "last_avg_rating",
        "send_timestamp",
    ]


admin.site.register(Question, QuestionAdmin)
admin.site.register(UploadQAfile, UploadAQfileAdmin)
# admin.site.register(DefaultQuestion,DefaultQuestionAdmin)
