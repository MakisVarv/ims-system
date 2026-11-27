from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
)

from modules.identity.policies import can_manage_catalog


class CatalogPermission(BasePermission):
    message = "Catalog changes require ADMIN or INVENTORY_MANAGER."

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.is_active
            and (request.method in SAFE_METHODS or can_manage_catalog(request.user))
        )
