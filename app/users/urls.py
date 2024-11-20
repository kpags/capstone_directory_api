from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
from .views import UsersViewset

router = DefaultRouter()

app_name = "users"
url_patterns = [
    path("", include(router.urls)),
]
