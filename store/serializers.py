from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from .models import (
    Cart,
    CartItem,
    Collection,
    Customer,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Review,
)


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


#########################################################################################
#  PRODUCT IMAGE


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return ProductImage.objects.create(product_id=product_id, **validated_data)


#########################################################################################
# REVIEW


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return Review.objects.create(product_id=product_id, **validated_data)


########################################################################################
# PRODUCT SIMPLE VERSION


class SimpleProductSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


#########################################################################################
#  CART ITEM


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerialiser()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


#########################################################################################
# CART

""" Product -> SimpleProductSerialiser ->  CartItemSerializer -> items
    'cart.items' returns a Manager Object """


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)  # get Product queryset

    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, cart):
        return sum(
            [item.quantity * item.product.unit_price for item in cart.items.all()]
        )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


#########################################################################################
# ADD ITEM TO THE CART


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product does not exist")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            # If the cart_item exists -> Update an existing item
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            # If cart_item doesn't exist -> Create a new item
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


#####################################################################################
# UPDATE A QUANTITY OF A PRODUCT IN THE CART ITEM


class UpdateCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["quantity"]


#####################################################################################
# CUSTOMER


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


#####################################################################################
# ORDER
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerialiser()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "unit_price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "customer_id", "placed_at", "payment_status", "items"]


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No card with the given ID was found")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]

            customer = Customer.objects.get(user_id=self.context["user_id"])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order
