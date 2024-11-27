from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter
from .views import UsersViewset, CapstoneGroupsViewset, LoginAPIView, ChangeCurrentPasswordAPIView, MeAPIView, ForgotPasswordAPIView

app_name = "users"

router = DefaultRouter()
router.register(r"user-view", views.UsersViewset, basename="user-view")
# router.register(r"user-profile", views.UserProfileViewset, basename="user-profile")
router.register(r"groups", views.CapstoneGroupsViewset, basename="groups")

urlpatterns = [
    path("me/", views.MeAPIView.as_view(), name="me"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path(
        "change-password/",
        views.ChangeCurrentPasswordAPIView.as_view(),
        name="change-password",
    ),
    path(
        "reset-password/",
        views.ForgotPasswordAPIView.as_view(),
        name="reset-password",
    ),
    path("", include(router.urls)),
]
