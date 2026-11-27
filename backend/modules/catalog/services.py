from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from modules.identity.policies import require_catalog_manager

from .models import Category, Product


def _persist(instance):
    instance.full_clean(validate_constraints=False)

    try:
        with transaction.atomic():
            instance.save()

    except IntegrityError as error:
        constraint = getattr(
            getattr(error.__cause__, "diag", None),
            "constraint_name",
            None,
        )

        field = {
            "catalog_product_sku_ci": "sku",
            "catalog_category_name_ci": "name",
        }.get(constraint)

        if field:
            raise ValidationError(
                {
                    field: "Already exists, ignoring letter case.",
                }
            ) from error

        raise

    return instance


def _active_category(category):
    try:
        return Category.objects.select_for_update().get(
            pk=category.pk,
            is_active=True,
        )

    except Category.DoesNotExist as error:
        raise ValidationError(
            {
                "category_id": "Choose an active category.",
            }
        ) from error


def create_category(actor, *, name):
    require_catalog_manager(actor)

    category = Category(name=name.strip())
    return _persist(category)


@transaction.atomic
def create_product(
    actor,
    *,
    sku,
    name,
    category,
    unit_code="PCS",
    is_active=True,
):
    require_catalog_manager(actor)

    if is_active is not True:
        raise ValidationError(
            {
                "is_active": "New products must start active.",
            }
        )

    product = Product(
        sku=sku.strip().upper(),
        name=name.strip(),
        category=_active_category(category),
        unit_code=unit_code.strip().upper(),
    )

    return _persist(product)


@transaction.atomic
def update_product(actor, product_id, **changes):
    require_catalog_manager(actor)

    product = Product.objects.select_for_update().get(
        pk=product_id,
    )

    for field in ("sku", "unit_code"):
        if field in changes:
            value = changes.pop(field).strip().upper()

            if value != getattr(product, field):
                raise ValidationError(
                    {
                        field: ("This field cannot change after creation."),
                    }
                )

    allowed_fields = {"name", "category", "is_active"}

    if set(changes) - allowed_fields:
        raise ValidationError("Unsupported product fields.")

    if "category" in changes:
        changes["category"] = _active_category(changes["category"])

    if "name" in changes:
        changes["name"] = changes["name"].strip()

    for field, value in changes.items():
        setattr(product, field, value)

    return _persist(product)
