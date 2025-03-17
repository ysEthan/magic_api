from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet, OrderViewSet, OrderItemViewSet

app_name = 'trade'

router = DefaultRouter()
router.register('shops', ShopViewSet)
router.register('orders', OrderViewSet)
router.register('order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 