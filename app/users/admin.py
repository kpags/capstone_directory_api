from django.contrib import admin
from .models import Users


class UsersAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)

    list_filter = ["role", "course", "specialization", "is_active"]
    search_fields = ["first_name", "last_name", "email", "student_number"]

admin.site.register(Users, UsersAdmin)