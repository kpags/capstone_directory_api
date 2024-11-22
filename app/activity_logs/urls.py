from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
from .views import ActivityLogsViewset

app_name = "activity_logs"

router = DefaultRouter()
router.register(r"logs", views.ActivityLogsViewset, basename="logs")

urlpatterns = [
    path("", include(router.urls)),
]
