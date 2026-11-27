from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from .filters import ProductFilter, StableOrderingFilter
from .models import Category, Product
from .permissions import CatalogPermission
from .serializers import CategorySerializer, ProductSerializer
from .services import (
    create_category,
    create_product,
    update_product,
)


def run_command(command, *args, **kwargs):
    try:
        return command(*args, **kwargs)

    except DjangoValidationError as error:
        detail = (
            error.message_dict if hasattr(error, "message_dict") else error.messages
        )

        raise ValidationError(detail) from error

    except Product.DoesNotExist as error:
        raise NotFound("Product not found.") from error


class CatalogPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class CatalogBaseViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    permission_classes = [
        IsAuthenticated,
        CatalogPermission,
    ]

    pagination_class = CatalogPagination

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    def get_success_headers(self, data):
        return {
            "Location": reverse(
                f"catalog:{self.basename}-detail",
                kwargs={"pk": data["id"]},
                request=self.request,
            ),
        }


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    CatalogBaseViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [
        SearchFilter,
        StableOrderingFilter,
    ]

    search_fields = ["name"]
    ordering_fields = ["id", "name"]
    ordering = ["id"]

    def perform_create(self, serializer):
        serializer.instance = run_command(
            create_category,
            self.request.user,
            **serializer.validated_data,
        )


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    CatalogBaseViewSet,
):
    queryset = Product.objects.select_related("category").all()

    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        StableOrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "sku",
        "name",
    ]

    ordering_fields = [
        "id",
        "sku",
        "name",
        "created_at",
        "is_active",
    ]

    ordering = ["id"]

    def perform_create(self, serializer):
        serializer.instance = run_command(
            create_product,
            self.request.user,
            **serializer.validated_data,
        )

    def perform_update(self, serializer):
        serializer.instance = run_command(
            update_product,
            self.request.user,
            product_id=serializer.instance.pk,
            **serializer.validated_data,
        )
