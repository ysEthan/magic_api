from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import ProductionCategory, ProductionOrder, ProductionStep, ProductionComment
from .serializers import (
    ProductionCategorySerializer, ProductionOrderSerializer,
    ProductionStepSerializer, ProductionCommentSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings


class ProductionCategoryViewSet(viewsets.ModelViewSet):
    """生产类目视图集"""
    queryset = ProductionCategory.objects.all()
    serializer_class = ProductionCategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category_type', 'is_active']
    search_fields = ['code', 'name', 'description']


class ProductionOrderFilter(filters.FilterSet):
    min_planned_start_date = filters.DateFilter(field_name='planned_start_date', lookup_expr='gte')
    max_planned_start_date = filters.DateFilter(field_name='planned_start_date', lookup_expr='lte')
    min_created_at = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    max_created_at = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    min_priority_order = filters.NumberFilter(field_name='priority_order', lookup_expr='gte')
    max_priority_order = filters.NumberFilter(field_name='priority_order', lookup_expr='lte')

    class Meta:
        model = ProductionOrder
        fields = {
            'order_type': ['exact'],
            'status': ['exact'],
            'priority': ['exact'],
            'priority_order': ['exact'],
            'category': ['exact'],
            'product': ['exact'],
            'manager': ['exact'],
            'created_by': ['exact'],
        }


class ProductionOrderViewSet(viewsets.ModelViewSet):
    """生产任务视图集"""
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    filterset_class = ProductionOrderFilter
    search_fields = ['code', 'description']
    ordering_fields = ['created_at', 'planned_start_date', 'priority', 'priority_order']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_serializer_context(self):
        """添加request到上下文"""
        context = super().get_serializer_context()
        return context

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新生产任务状态"""
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(ProductionOrder.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'success'})
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def update_priority_order(self, request, pk=None):
        """更新任务优先级排序"""
        order = self.get_object()
        new_priority_order = request.data.get('priority_order')
        
        try:
            new_priority_order = int(new_priority_order)
            if new_priority_order < 0:
                return Response(
                    {'error': '优先级排序值不能小于0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order.priority_order = new_priority_order
            order.save()
            return Response({
                'status': 'success',
                'priority_order': new_priority_order
            })
        except (TypeError, ValueError):
            return Response(
                {'error': '无效的优先级排序值'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """上传主图"""
        order = self.get_object()
        if 'main_image' not in request.FILES:
            return Response(
                {'error': '请选择要上传的图片'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['main_image']
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            return Response(
                {'error': '不支持的图片格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if file.size > settings.MAX_UPLOAD_SIZE:
            return Response(
                {'error': '图片大小超过限制'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.main_image = file
        order.save()
        return Response({
            'status': 'success',
            'main_image_url': request.build_absolute_uri(order.main_image.url)
        })


class ProductionStepViewSet(viewsets.ModelViewSet):
    """生产步骤视图集"""
    queryset = ProductionStep.objects.all()
    serializer_class = ProductionStepSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['order', 'step_type', 'status', 'operator']
    search_fields = ['name', 'description']
    ordering_fields = ['sequence', 'start_time', 'end_time']

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新步骤状态"""
        step = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(ProductionStep.STATUS_CHOICES):
            step.status = new_status
            step.save()
            return Response({'status': 'success'})
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductionCommentViewSet(viewsets.ModelViewSet):
    """生产评论视图集"""
    queryset = ProductionComment.objects.all()
    serializer_class = ProductionCommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['order', 'step', 'comment_type', 'author']
    search_fields = ['content']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 