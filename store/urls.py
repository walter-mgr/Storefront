from django.urls import path, include
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
router.register("collections", views.CollectionViewSet)
router.register("products", views.ProductViewSet, basename="products")
router.register("orders", views.OrderViewSet)
router.register("carts", views.CartViewSet, basename="carts")


products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register(
    "reviews", viewset=views.ReviewViewSet, basename="products-reviews"
)

carts_router = routers.NestedDefaultRouter(router, "carts")
carts_router.register("items", viewset=views.CartItemViewSet, basename="carts-items")

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(products_router.urls)),
    path(r"", include(carts_router.urls)),
]
