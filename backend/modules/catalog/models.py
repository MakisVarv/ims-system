from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower, Trim


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                Lower(Trim("name")),
                name="catalog_category_name_ci",
            ),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(
        max_length=64,
        validators=[
            RegexValidator(
                r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
                "Use letters, numbers, dots, underscores or hyphens.",
            ),
        ],
    )

    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    unit_code = models.CharField(
        max_length=16,
        default="PCS",
        validators=[
            RegexValidator(
                r"^[A-Za-z][A-Za-z0-9_]*$",
                "Use a unit code such as PCS or KG.",
            ),
        ],
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                Lower(Trim("sku")),
                name="catalog_product_sku_ci",
            ),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"
