from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from tags.models import TaggedItem
from store.models import Product


class TagInline(GenericTabularInline):
    autocomplete_fields = ["tag"]
    model = TaggedItem
    extra = 0
    min_num = 1


class CoreProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, CoreProductAdmin)
