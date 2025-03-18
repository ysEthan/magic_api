from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('suppliers', views.SupplierViewSet)
router.register('orders', views.PurchaseOrderViewSet)
router.register('order-items', views.PurchaseOrderItemViewSet, basename='order-items')

app_name = 'purchase'

urlpatterns = [
    path('', include(router.urls)),
] 