from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CapstoneProjects

class CapstoneProjectsSerializer(serializers.ModelSerializer):
    acm_paper = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = CapstoneProjects
        fields = "__all__"
        depth = 1
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["acm_paper"] = instance.acm_paper
        
        return representation
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        http_method = self.context.get("request", None)
        
        if http_method and http_method in ["put", "patch", "PUT", "PATCH"]:
            self.fields.pop('is_best_project', None)
            self.fields.pop('is_approved', None)
        
class CapstoneProjectsCustomSerializer(serializers.Serializer):
    capstone_group_id = serializers.CharField(required=False) # get UUID of the group
    title = serializers.CharField()
    ip_regristration = serializers.CharField(required=False)
    acm_paper = serializers.FileField(required=False)
    full_document = serializers.CharField(required=False)
    pubmat = serializers.CharField(required=False)
    approval_form = serializers.CharField(required=False)
    source_code = serializers.CharField(required=False)
    members = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    date_published = serializers.DateField(required=False)
    status = serializers.CharField(required=False)
    course = serializers.CharField(required=True)
    specialization = serializers.CharField(required=True)

class CapstoneProjectApprovalSerializer(serializers.Serializer):
    project_id = serializers.CharField()
    is_approved = serializers.CharField(allow_null=True, required=False)
    
class CapstoneProjectBestProjectSerializer(serializers.Serializer):
    project_id = serializers.CharField()
    is_best_project = serializers.BooleanField()