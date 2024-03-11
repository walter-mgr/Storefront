from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, F, Q, ExpressionWrapper
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from .filters import ProductFilter
from .models import Product, Collection, Order, OrderItem, Review, Cart, CartItem
from .serializers import (
    ProductSerializer,
    CollectionSerializer,
    OrderSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
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
# ORDER LIST: http://127.0.0.1:8000/store/orders/


class OrderViewSet(ReadOnlyModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderSerializer

    def get_serializer_context(self):
        return {"request": self.request}


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

###############################################################################
# CART ITEM, ADD ITEM TO THE CART


class CartItemViewSet(ModelViewSet):
    # serializer_class = CartItemSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    def get_queryset(self):
        return CartItem.objects.select_related("product").filter(
            cart_id=self.kwargs["cart_pk"]
        )
