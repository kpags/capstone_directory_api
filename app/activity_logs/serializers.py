from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import ActivityLogs
from users.serializers import UsersSerializer

class ActivityLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogs
        fields = "__all__"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        user_serialized_data = UsersSerializer(instance.user).data
        representation["user"] = user_serialized_data
        
        return representation