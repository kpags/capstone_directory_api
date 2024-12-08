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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
@swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "search",
            openapi.IN_QUERY,
            description="Search by actor's first name, last name, email, or actions",
            type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            description="Page Filter",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
    ],
    responses={
        200: ActivityLogsSerializer(many=True),
    }
)
class ActivityLogsViewset(viewsets.ModelViewSet):
    queryset = ActivityLogs.objects.order_by("-created_at")
    serializer_class = ActivityLogsSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'action', 'actor_name']
    http_method_names = ["get"]
