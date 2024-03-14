from typing import Any
from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import ngettext
from django.utils.html import format_html
from django.utils.http import urlencode
from .models import Collection, Product, Order, OrderItem, Customer


###########################################################################################
# COLLECTION
###########################################################################################
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "products_count"]
    search_fields = ["title"]

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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Form
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["promotions"]
    search_fields = ["title"]

    # Page
    actions = ["clear_inventory"]
    list_display = [
        "id",
        "title",
        "unit_price",
        "inventory_status",
        "inventory",
        "collection_title",
    ]
    list_editable = ["unit_price", "inventory"]
    list_filter = ["collection", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]

    def collection_title(self, product: Product):
        return product.collection

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            ngettext(
                "%d product was successfully updated",
                "%d products were successfully updated",
                updated_count,
            )
            % updated_count,
            messages.SUCCESS,
        )

    # Computed field -> target field: "inventory"
    @admin.display(ordering="inventory")
    def inventory_status(self, product: Product):
        if product.inventory < 5:
            return "LOW"
        if product.inventory >= 5 and product.inventory < 15:
            return "MIDDLE"
        return "OK"


######################################################################################
# CUSTOMER


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "membership"]
    list_editable = ["membership"]
    list_per_page = 10
    search_fields = ["last_name__istartswith"]

    @admin.display(description="full_name")
    def full_name(self, customer: Customer):
        return f"{customer.first_name} {customer.last_name}"


######################################################################################
# ORDER ITEM


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    model = OrderItem
    min_num = 1
    max_num = 10
    extra = 0


###########################################
# ORDER


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Form
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]

    # Page
    list_display = ["id", "placed_at", "customer"]
    list_per_page = 10
    ordering = ["-placed_at"]
