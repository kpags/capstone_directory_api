from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
from .views import NotificationsViewset

app_name = "notifications"

router = DefaultRouter()
router.register(r"", views.NotificationsViewset, basename="")

urlpatterns = [
    path("", include(router.urls)),
]
