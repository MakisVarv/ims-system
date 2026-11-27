from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter

from .models import Category, Product


class ProductFilter(filters.FilterSet):
    category_id = filters.ModelChoiceFilter(
        field_name="category",
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Product

        fields = [
            "category_id",
            "is_active",
        ]


class StableOrderingFilter(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        ordering = list(super().get_ordering(request, queryset, view) or ["id"])

        has_id = any(field.lstrip("-") in {"id", "pk"} for field in ordering)

        if not has_id:
            ordering.append("id")

        return ordering
