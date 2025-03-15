from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, BrandViewSet, CategoryViewSet, SPUViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('brands', BrandViewSet)
router.register('categories', CategoryViewSet)
router.register('spus', SPUViewSet)

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
] 