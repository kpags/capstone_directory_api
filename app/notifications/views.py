from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notifications, NotificationRead
from users.models import Users
from .serializers import (NotificationsSerializer, NotificationReadCustomSerializer)
from utils.permissions import IsActive, IsAdmin
from django.db.models import Q, OuterRef, When, Case, BooleanField
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
class NotificationsViewset(viewsets.ModelViewSet):
    http_method_names = ["get", "post"]
    
    def get_serializer_class(self):
        path = self.request.path
        
        if "mark-as-read" in path:
            return NotificationReadCustomSerializer
        
        return NotificationsSerializer
    def get_queryset(self):
        user = self.request.instance
        role = user.role
        
        notifications_read = NotificationRead.objects.filter(notification__id=OuterRef("id")).values_list("notification__id")
    
        if role.lower() == "student":
            queryset = Notifications.objects.filter(
                Q(to_user=user) | Q(to_group=user.group)
            )
        elif role.lower() in ["admin", "administrator"]:
            queryset = Notifications.objects.order_by('-created_at')
        else:
            queryset = Notifications.objects.filter(to_user=user)
            
        return queryset.annotate(
            is_read=Case(
                When(id__in=notifications_read, then=True), 
                default=False, output_field=BooleanField()
            )
        ).order_by('-created_at')
    
    @swagger_auto_schema(
        request_body=None,
        responses={
            202: "No need to use this endpoint.",
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=NotificationReadCustomSerializer,
        responses={
            200: "Notification marked as read.",
            404: "Notification does not exist and cannot be marked as read."
        }
    )
    @action(detail=False, methods=["POST"], permission_classes=[IsAdmin], serializer_class=NotificationReadCustomSerializer, url_path="mark-as-read")
    def mark_notification_as_read(self, request):
        data = request.data
        user = request.instance
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        try:
            notification = Notifications.objects.get(id=validated_data["notification_id"])
            notification_read = NotificationRead(notification=notification, reader=user)
            notification_read.save()
            
            return Response({
                "message": "Notification marked as read."
            }, status=status.HTTP_200_OK)
        except Notifications.DoesNotExist:
            return Response({
                "message": "Notification does not exist and cannot be marked as read."
            }, status=status.HTTP_404_NOT_FOUND)
