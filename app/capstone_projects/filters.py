from django_filters import rest_framework as filters

from .models import CapstoneProjects

class CapstoneProjectsFilter(filters.FilterSet):
    is_best_project = filters.BooleanFilter(field_name="is_best_project")
    is_approved = filters.BooleanFilter(field_name="is_approved")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    keywords = filters.CharFilter(method="filter_by_keywords")
    
    class Meta:
        model = CapstoneProjects
        fields = ['keywords', 'status', 'is_approved', 'is_best_project']
        
    def filter_by_keywords(self, queryset, name, value):
        array_values = value.split(",")
        
        return queryset.filter(keywords__overlap=array_values)