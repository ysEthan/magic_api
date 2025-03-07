from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.ProductionCategoryViewSet)
router.register('orders', views.ProductionOrderViewSet)
router.register('steps', views.ProductionStepViewSet)
router.register('comments', views.ProductionCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 