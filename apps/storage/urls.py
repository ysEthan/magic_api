from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, InventoryViewSet,
    StockInViewSet, StockOutViewSet
)

router = DefaultRouter()
router.register('warehouses', WarehouseViewSet)
router.register('inventories', InventoryViewSet)
router.register('stock-ins', StockInViewSet)
router.register('stock-outs', StockOutViewSet)

app_name = 'storage'

urlpatterns = [
    path('', include(router.urls)),
] 