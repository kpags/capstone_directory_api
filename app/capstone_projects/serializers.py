from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CapstoneProjects

class CapstoneProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapstoneProjects
        fields = "__all__"
        depth = 1
        
class CapstoneProjectsCustomSerializer(serializers.Serializer):
    capstone_group_id = serializers.CharField() # get UUID of the group
    title = serializers.CharField()
    ip_regristration = serializers.CharField(required=False)
    acm_paper = serializers.FileField(required=False)
    full_document = serializers.CharField(required=False)
    pubmat = serializers.CharField(required=False)
    approval_form = serializers.CharField(required=False)
    source_code = serializers.CharField(required=False)
    members = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    date_published = serializers.DateField(required=False)
    is_approved = serializers.BooleanField(required=False)
    status = serializers.CharField(required=False)
    is_best_project = serializers.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        user = self.context.get('user', None)
        
        if user and user.role.lower() not in ['admin', 'administrator']:
            self.fields.pop('is_approved')
            self.fields.pop('status')
            self.fields.pop('is_best_project')
