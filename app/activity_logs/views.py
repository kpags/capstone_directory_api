from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ActivityLogs
from users.models import Users
from .serializers import (ActivityLogsSerializer)
from utils.permissions import IsActive, IsAdmin

# Create your views here.
class ActivityLogsViewset(viewsets.ModelViewSet):
    queryset = ActivityLogs.objects.order_by("-created_at")
    serializer_class = ActivityLogsSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    http_method_names = ["get"]
