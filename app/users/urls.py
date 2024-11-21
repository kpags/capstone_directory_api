from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
from .views import UsersViewset, LoginAPIView, ChangeCurrentPasswordAPIView

app_name = "users"

router = DefaultRouter()
router.register(r"user-viewset", views.UsersViewset, basename="user-viewset")

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path(
        "change-password/",
        views.ChangeCurrentPasswordAPIView.as_view(),
        name="change-password",
    ),
    path("", include(router.urls)),
]
