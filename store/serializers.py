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
