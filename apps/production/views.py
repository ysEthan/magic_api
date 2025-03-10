from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import ProductionCategory, ProductionOrder, ProductionStep, ProductionComment, ProductionChannel
from .serializers import (
    ProductionCategorySerializer, ProductionOrderSerializer,
    ProductionStepSerializer, ProductionCommentSerializer,
    ProductionChannelSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth


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

    @action(detail=False, methods=['get'])
    def next_id(self, request):
        """获取下一个任务编号"""
        next_code = ProductionOrder.generate_next_code()
        print(next_code)
        return Response({
            'code': next_code
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


class ProductionChannelViewSet(viewsets.ModelViewSet):
    """生产渠道视图集"""
    queryset = ProductionChannel.objects.all()
    serializer_class = ProductionChannelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name', 'description']


class ProductionReportViewSet(viewsets.ViewSet):
    """生产报表视图集"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取报表汇总数据"""
        # 获取所有订单
        orders = ProductionOrder.objects.all()
        
        # 计算总数和状态分布
        total_orders = orders.count()
        status_counts = orders.values('status').annotate(count=Count('id'))
        status_distribution = {
            'pending': 0,
            'in_progress': 0,
            'completed': 0,
            'cancelled': 0
        }
        for item in status_counts:
            status_distribution[item['status']] = item['count']
            
        # 计算完成率
        completed_count = status_distribution['completed']
        completion_rate = (completed_count / total_orders * 100) if total_orders > 0 else 0
        
        # 计算计划量和完成量
        total_planned = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_completed = orders.filter(
            status='completed'
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        return Response({
            'total_orders': total_orders,
            'completion_rate': round(completion_rate, 2),
            'total_planned': total_planned,
            'total_completed': total_completed,
            'status_distribution': status_distribution
        })

    @action(detail=False, methods=['get'])
    def trend(self, request):
        """获取趋势数据"""
        # 获取请求参数
        trend_type = request.query_params.get('type', 'daily')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        category = request.query_params.get('category')
        
        # 验证日期参数
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except (TypeError, ValueError):
            return Response(
                {'error': '无效的日期格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 构建基础查询
        orders = ProductionOrder.objects.all()
        if category:
            orders = orders.filter(category_id=category)
            
        # 根据趋势类型选择日期截断方式
        date_trunc = {
            'daily': TruncDate,
            'weekly': TruncWeek,
            'monthly': TruncMonth
        }.get(trend_type, TruncDate)
        
        # 获取新建任务数据
        new_orders = orders.filter(
            created_at__date__range=[start_date, end_date]
        ).annotate(
            date=date_trunc('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # 获取完成任务数据
        completed_orders = orders.filter(
            status='completed',
            updated_at__date__range=[start_date, end_date]
        ).annotate(
            date=date_trunc('updated_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # 生成日期列表
        dates = []
        new_orders_data = []
        completed_orders_data = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            dates.append(date_str)
            
            # 查找当天的新建任务数
            new_count = next(
                (item['count'] for item in new_orders if item['date'].strftime('%Y-%m-%d') == date_str),
                0
            )
            new_orders_data.append(new_count)
            
            # 查找当天的完成任务数
            completed_count = next(
                (item['count'] for item in completed_orders if item['date'].strftime('%Y-%m-%d') == date_str),
                0
            )
            completed_orders_data.append(completed_count)
            
            current_date += timedelta(days=1)
            
        return Response({
            'dates': dates,
            'new_orders': new_orders_data,
            'completed_orders': completed_orders_data
        }) 