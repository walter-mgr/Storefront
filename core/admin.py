from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin, ProductImageInline
from tags.models import TaggedItem
from store.models import Product
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )


class TagInline(GenericTabularInline):
    autocomplete_fields = ["tag"]
    model = TaggedItem
    extra = 0
    min_num = 1


class CoreProductAdmin(ProductAdmin):
    inlines = [TagInline, ProductImageInline]


admin.site.unregister(Product)
admin.site.register(Product, CoreProductAdmin)
