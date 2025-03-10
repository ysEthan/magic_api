from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.ProductionCategoryViewSet)
router.register('orders', views.ProductionOrderViewSet)
router.register('steps', views.ProductionStepViewSet)
router.register('comments', views.ProductionCommentViewSet)
router.register(r'channels', views.ProductionChannelViewSet)
router.register('reports', views.ProductionReportViewSet, basename='production-reports')

urlpatterns = [
    path('', include(router.urls)),
] 