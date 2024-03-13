from typing import Any
from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from . import models


###########################################################################################
# COLLECTION
###########################################################################################
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "products_count"]

    # Add links to the product_count field
    @admin.display(description="products_count")
    def products_count(self, collection):

        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )

        return format_html("<a href={}>{}</a>", url, collection.products_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count("products"))


###########################################################################################
# PRODUCT
###########################################################################################


# ========================
# Custom Filter
# ========================


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [("<5", "Low"), (">= 5 and < 15", "Middle"), (">=15", "Ok")]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "<5":
            return queryset.filter(inventory__lt=5)
        if self.value() == ">= 5 and < 15":
            return queryset.filter(inventory__gte=5, inventory__lt=15)
        if self.value() == ">=15":
            return queryset.filter(inventory__gte=15)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # Form
    readonly_fields = ["promotions"]

    # Page
    list_display = ["title", "unit_price", "inventory_status", "inventory"]
    list_editable = ["unit_price", "inventory"]
    list_filter = ["collection", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]

    # Computed field -> target field: "inventory"
    @admin.display(ordering="inventory")
    def inventory_status(self, product: models.Product):
        if product.inventory < 5:
            return "LOW"
        if product.inventory >= 5 and product.inventory < 15:
            return "MIDDLE"
        return "OK"


######################################################################################
# CUSTOMER


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "membership"]
    list_editable = ["membership"]
    list_per_page = 10

    @admin.display(description="full_name")
    def full_name(self, customer: models.Customer):
        return f"{customer.first_name} {customer.last_name}"


######################################################################################
# ORDER


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]
