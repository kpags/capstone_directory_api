from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
from .views import CapstoneProjectsViewset

app_name = "capstone_projects"

router = DefaultRouter()
router.register(r"projects", views.CapstoneProjectsViewset, basename="projects")

urlpatterns = [
    path("", include(router.urls)),
]
