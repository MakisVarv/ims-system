from django.core.exceptions import PermissionDenied


class Role:
    ADMIN = "ADMIN"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    WAREHOUSE_OPERATOR = "WAREHOUSE_OPERATOR"
    PURCHASING_OFFICER = "PURCHASING_OFFICER"
    PURCHASING_MANAGER = "PURCHASING_MANAGER"
    AUDITOR = "AUDITOR"

    ALL = (
        ADMIN,
        INVENTORY_MANAGER,
        WAREHOUSE_OPERATOR,
        PURCHASING_OFFICER,
        PURCHASING_MANAGER,
        AUDITOR,
    )


def get_roles(user) -> list[str]:
    if not user.is_authenticated or not user.is_active:
        return []

    roles = set(
        user.groups.filter(
            name__in=Role.ALL,
        ).values_list("name", flat=True)
    )

    if user.is_superuser:
        roles.add(Role.ADMIN)

    return sorted(roles)


def can_manage_catalog(user) -> bool:
    allowed_roles = {
        Role.ADMIN,
        Role.INVENTORY_MANAGER,
    }

    return bool(allowed_roles & set(get_roles(user)))


def require_catalog_manager(user):
    if not can_manage_catalog(user):
        raise PermissionDenied("Catalog changes require ADMIN or INVENTORY_MANAGER.")
