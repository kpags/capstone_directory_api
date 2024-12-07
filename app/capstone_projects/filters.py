from django_filters import rest_framework as filters
from django.db.models import Q
from .models import CapstoneProjects

class CapstoneProjectsFilter(filters.FilterSet):
    is_best_project = filters.BooleanFilter(field_name="is_best_project")
    is_approved = filters.BooleanFilter(field_name="is_approved")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    sort_by = filters.CharFilter(method="filter_by_sort_type")
    is_ip_registered = filters.CharFilter(method="filter_by_is_ip_registered")
    search = filters.CharFilter(method="filter_by_search")
    course = filters.CharFilter(method="filter_by_course")
    specialization = filters.CharFilter(method="filter_by_specialization")
    
    class Meta:
        model = CapstoneProjects
        fields = ['search', 'status', 'is_approved', 'is_best_project', 'sort_by', 'is_ip_registered', 'course', 'specialization']
    
    def filter_by_course(self, queryset, name, value):
        return queryset.filter(Q(capstone_group__course__iexact=value) | Q(course__iexact=value))
    
    def filter_by_specialization(self, queryset, name, value):
        return queryset.filter(Q(capstone_group__specialization__iexact=value) | Q(specialization__iexact=value))
    
    def filter_by_search(self, queryset, name, value):
        array_values = value.lower().split(" ")
        
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(capstone_group__name=value) | 
            Q(capstone_group__academic_year=value) | 
            Q(keywords__overlap=array_values)
        )
    
    def filter_by_sort_type(self, queryset, name, value):
        if value.lower() == "newest":
            return queryset.order_by('-created_at')
        elif value.lower() == "oldest":
            return queryset.order_by('created_at')
        elif value.lower() == "alphabetical_asc":
            return queryset.order_by('title')
        elif value.lower() == "alphabetical_desc":
            return queryset.order_by('-title')
        else:
            return queryset
        
    def filter_by_is_ip_registered(self, queryset, name, value):
        if value.lower() == "true" or value == True:
            return queryset.exclude(ip_registration=None).exclude(ip_registration="")
        elif value.lower() == "false" or value == False:
            return queryset.filter(Q(ip_registration=None) | Q(ip_registration=""))
        else:
            return queryset