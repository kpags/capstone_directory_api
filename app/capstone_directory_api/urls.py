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
        title="Capstone Directory API Documentation",
        default_version="v1",
        description="API documentation for Capstone Directory API",
    ),
    public=True,
    # permission_classes=(IsAdmin,) if ENVIRONMENT == "PROD" else (),
    permission_classes=(),
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

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
