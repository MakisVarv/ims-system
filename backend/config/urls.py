from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import IsAdminUser

from .health import live, ready

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "health/live/",
        live,
        name="health-live",
    ),
    path(
        "health/ready/",
        ready,
        name="health-ready",
    ),
    path(
        "api/v1/schema/",
        SpectacularAPIView.as_view(
            permission_classes=[IsAdminUser],
        ),
        name="schema",
    ),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            permission_classes=[IsAdminUser],
        ),
        name="swagger-ui",
    ),
    path("api/v1/auth/", include("modules.identity.urls")),
]
