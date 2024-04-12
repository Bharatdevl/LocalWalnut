from django.contrib import admin

from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "company",
        "is_opted",
    ]
    list_display_links = None

    def get_company(self, obj):
        if obj:
            try:
                return obj.company.company.name
            except:
                pass

    def created_by(self, obj):
        if obj:
            try:
                return obj.company.first_name
            except:
                pass

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Employee, EmployeeAdmin)
