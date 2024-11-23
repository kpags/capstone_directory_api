from django.contrib import admin
from .models import Notifications

# Register your models here.
class NotificationsAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)
        
    search_fields = ['actor__email', 'actor__first_name', 'actor__last_name', 
                     "to_group__number", "to_group__course", "to_group__specialization",
                     "to_user__email", "to_user__first_name", "to_user__last_name"]
    
admin.site.register(Notifications, NotificationsAdmin)