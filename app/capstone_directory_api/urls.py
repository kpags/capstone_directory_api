from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from utils.permissions import IsAdmin
import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "DEV")

schema_view = get_schema_view(
    openapi.Info(
        title="Dropify PH API Documentation",
        default_version="v1",
        description="API documentation for Dropify PH API",
    ),
    public=True,
    permission_classes=(IsAdmin,) if ENVIRONMENT == "PROD" else (),
)

urlpatterns = (
    [
        path(settings.ADMIN_URL, admin.site.urls),
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
        ),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)


urlpatterns += [
    re_path(
        r"api/users/",
        include("users.urls", namespace="users"),
    ),
    re_path(
        r"api/capstone-projects/",
        include("capstone_projects.urls", namespace="capstone_projects"),
    ),
    re_path(
        r"api/activity-logs/",
        include("activity_logs.urls", namespace="activity_logs"),
    ),
     re_path(
        r"api/notifications/",
        include("notifications.urls", namespace="notifications"),
    ),
]
