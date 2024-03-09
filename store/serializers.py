from decimal import Decimal
from rest_framework import serializers
from .models import Product, Collection, Order, OrderItem, Review, Cart, CartItem


#######################################################################################
# COLLECTION


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]

    products_count = serializers.IntegerField(read_only=True)


#######################################################################################
# PRODUCT


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "unit_price",
            "price_with_tax",
            "inventory",
            "collection",
            "order_id",
        ]

    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(), view_name="collection-detail"
    )
    order_id = serializers.IntegerField(read_only=True)

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.2)


#####################################################################################
# ORDER


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "placed_at",
            "product",
            "quantity",
            "unit_price",
            "total",
            "order_id",
        ]

    product = serializers.StringRelatedField()
    quantity = serializers.IntegerField(read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )
    total = serializers.SerializerMethodField(method_name="calculate_total")
    order_id = serializers.IntegerField(read_only=True)

    def calculate_total(self, obj: OrderItem):
        if obj.product == None:
            return 0
        return obj.quantity * obj.unit_price


#########################################################################################
# REVIEW


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    def create(self, validated_data):
        product_pk = self.context["product_pk"]
        return Review.objects.create(product_id=product_pk, **validated_data)


#########################################################################################
# CART


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items"]


#########################################################################################
#  CARTITEM

"""
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "quantity", "cart_id", "product_id"]
"""
