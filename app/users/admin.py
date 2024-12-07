from django.contrib import admin
from .models import Users, CapstoneGroups, TechnicalAdvisorGroups


class UsersAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)

    list_filter = ["role", "course", "specialization", "is_active"]
    search_fields = ["first_name", "last_name", "email", "student_number"]

admin.site.register(Users, UsersAdmin)

class CapstoneGroupsAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)

    list_filter = ["academic_year", "course", "specialization"]
    search_fields = ["name"]

admin.site.register(CapstoneGroups, CapstoneGroupsAdmin)

class TechnicalAdvisorGroupsGroupsAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)

    list_filter = ["group__academic_year", "group__course", "group__specialization"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]

admin.site.register(TechnicalAdvisorGroups, TechnicalAdvisorGroupsGroupsAdmin)