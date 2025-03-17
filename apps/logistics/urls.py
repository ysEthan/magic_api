from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CarrierViewSet, ServiceViewSet,
    PackageViewSet, TrackingViewSet
)

app_name = 'logistics'

router = DefaultRouter()
router.register('carriers', CarrierViewSet)
router.register('services', ServiceViewSet)
router.register('packages', PackageViewSet)
router.register('tracking', TrackingViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 