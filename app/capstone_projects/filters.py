from django_filters import rest_framework as filters

from .models import CapstoneProjects

class CapstoneProjectsFilter(filters.FilterSet):
    is_best_project = filters.BooleanFilter(field_name="is_best_project")
    is_approved = filters.BooleanFilter(field_name="is_approved")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    keywords = filters.CharFilter(method="filter_by_keywords")
    sort_by = filters.CharFilter(method="filter_by_sort_type")
    
    class Meta:
        model = CapstoneProjects
        fields = ['keywords', 'status', 'is_approved', 'is_best_project', 'sort_by']
        
    def filter_by_keywords(self, queryset, name, value):
        array_values = value.split(",")
        
        return queryset.filter(keywords__overlap=array_values)
    
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