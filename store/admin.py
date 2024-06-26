from typing import Any
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count, F
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import ngettext
from django.utils.html import format_html
from django.utils.http import urlencode
from .models import Collection, Customer, Product, ProductImage, Order, OrderItem
from tags.models import TaggedItem


###########################################################################################
# COLLECTION


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    readonly_fields = ["featured_product"]
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


# ========================
# Product Custom Filter
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


# ============================================
# TODO: add links to the Collection


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ["thumbnail"]

    def thumbnail(self, instance: ProductImage):
        if instance.image.name != "":
            return format_html(f"<img src='{instance.image.url}' class='thumbnail' />")
        return ""


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Form
    autocomplete_fields = ["collection"]
    inlines = [ProductImageInline]
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

    class Media:
        css = {"all": ["store/styles.css"]}


######################################################################################
# CUSTOMER


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    list_display = ["id", "first_name", "last_name", "membership", "orders"]
    list_editable = ["membership"]
    list_per_page = 10
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    """
    @admin.display(description="full_name")
    def full_name(self, customer: Customer):
        return f"{customer.user.first_name} {customer.user.last_name}"
"""

    @admin.display(ordering="orders")
    def orders(self, order):
        return order.orders

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders=Count("order"))


# TODO: Calculate total sum of money of all orders that each Customer has made


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
    list_display = ["placed_at", "customer"]
    list_per_page = 10
    ordering = ["-placed_at"]
