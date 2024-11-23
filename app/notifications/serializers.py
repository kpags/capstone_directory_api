from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Notifications, NotificationRead

class NotificationsSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Notifications
        fields = "__all__"
        depth = 1
        
    def get_is_read(self, obj):
        return obj.is_read
        
class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRead
        fields = "__all__"
        depth = 1
        
class NotificationReadCustomSerializer(serializers.Serializer):
    notification_id = serializers.CharField(max_length=1000)