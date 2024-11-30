from django.contrib import admin
from .models import CapstoneProjects

# Register your models here.
class CapstoneProjectsAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        # Dynamically set list_display with all field names
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)
        
    list_filter = ['status', 'is_approved', 'is_best_project']
    search_fields = ['title', 'capstone_group__name', 'capstone_group__academic_year']
    
admin.site.register(CapstoneProjects, CapstoneProjectsAdmin)