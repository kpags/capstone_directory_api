from django.contrib import admin
from .models import ActivityLogs

# Register your models here.
class ActivityLogsAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)
    
    search_fields = ['user__first_name', 'user__last_name', 'user__email', "action", "created_at"]
    
admin.site.register(ActivityLogs, ActivityLogsAdmin)