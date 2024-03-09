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


########################################################################################
# PRODUCT SIMPLE VERSION


class SimpleProductSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price", "inventory"]


"""
    total_price = serializers.DecimalField(
        max_digits=2, decimal_places=2, read_only=True
    )
"""

#########################################################################################
#  CART ITEM


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerialiser()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity"]

    # total_price = serializers.SerializerMethodField(method_name="calculate_total")
    # total_price = serializers.IntegerField()


"""
    def calculate_total(self, product: Product, items: CartItem):
        return product.unit_price * items.quantity
        pass
"""

#########################################################################################
# CART


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ["id", "items"]

    # total_price = serializers.IntegerField()
