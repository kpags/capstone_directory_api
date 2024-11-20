from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = "users"
url_patterns = [
    path("", include(router.urls)),
]
