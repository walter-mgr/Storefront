from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, F, Q, ExpressionWrapper
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    DjangoModelPermissions,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from .filters import ProductFilter
from .models import (
    Product,
    Collection,
    Order,
    OrderItem,
    Review,
    Cart,
    CartItem,
    Customer,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    ProductSerializer,
    CollectionSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    CustomerSerializer,
)

# DJANGO_REST_FRAMEWORK_DOCS = https://www.django-rest-framework.org/
# DJANGO_FILTER_23.5_DOCS = https://django-filter.readthedocs.io/en/stable/guide/usage.html

##############################################################################
# PRODUCT SET: http://127.0.0.1:8000/store/products/

"""Add related_name='products' into the 'collection' field in the Product model"""


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {"Error: cannot be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)


#############################################################################
#  COLLECTION SET: http://127.0.0.1:8000/store/collections/

"""Add related_name='order_items' into the 'product' field in the OrderItem model"""


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "Error": "Collection cannot be deleted because it is associated with a product"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


###############################################################################
# REVIEW / NESTED IN PRODUCT

"""Add related_name='reviews' into the 'product' field in the Review model"""


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_pk": self.kwargs["product_pk"]}


###############################################################################
# CART

# http://127.0.0.1:8000/store/carts/
# DOCUMENTATION GITHUB: https://github.com/alanjds/drf-nested-routers

"""Add related_name='items' into the 'product' field in the CartItem model"""


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer

    def get_serialiser_context(self):
        return {"request": self.request}


###############################################################################
# TEST CARTS

# 1. 89e4beddd2de4de5b7f8ac59e97d9fb5
# 2. 6a534217da3c4982b008bf23768e8da3
# 3. a784f2bda0ec4c3d92ad94e5b96388b9

###############################################################################
# CART ITEM, ADD ITEM TO THE CART


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {
            "cart_id": self.kwargs["cart_pk"],
        }

    def get_queryset(self):
        return CartItem.objects.select_related("product").filter(
            cart_id=self.kwargs["cart_pk"]
        )


################################################################################


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


###############################################################################
# ORDER LIST: http://127.0.0.1:8000/store/orders/
# New test cart ID: 570cd5f4-09ef-470d-9348-dff0d8ff3a63
# New test cart ID: a91539f7-3659-47be-88ac-03819d223c94 - empty
"""Add related_name='items' into the 'order' field in the OrderItem model"""


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serialiser = CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.pk}
        )
        serialiser.is_valid(raise_exception=True)
        order = serialiser.save()

        serialiser = OrderSerializer(order)
        return Response(serialiser.data)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        if self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only("id").get(user_id=user.pk)
        return Order.objects.filter(customer_id=customer_id)
