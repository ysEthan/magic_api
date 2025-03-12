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
from django.db.models import Count, Q, Sum, F
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

    def perform_update(self, serializer):
        # 保持原有的 created_by
        instance = serializer.instance
        serializer.save(created_by=instance.created_by)

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

    @action(detail=True, methods=['get'])
    def current_step(self, request, pk=None):
        """获取当前正在进行的步骤"""
        order = self.get_object()
        current_step = ProductionStep.objects.filter(
            order=order,
            status='in_progress'
        ).order_by('sequence').first()
        
        if not current_step:
            # 如果没有进行中的步骤，获取第一个待处理的步骤
            current_step = ProductionStep.objects.filter(
                order=order,
                status='pending'
            ).order_by('sequence').first()
        
        if current_step:
            serializer = ProductionStepSerializer(current_step)
            return Response(serializer.data)
        
        return Response({
            'message': '没有正在进行或待处理的步骤'
        })


class ProductionStepViewSet(viewsets.ModelViewSet):
    """生产步骤视图集"""
    queryset = ProductionStep.objects.all()
    serializer_class = ProductionStepSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['order', 'step_name', 'status', 'operator', 'contractor']
    search_fields = ['description', 'contractor']
    ordering_fields = ['sequence', 'start_time', 'end_time']

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新步骤状态"""
        step = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(ProductionStep.STATUS_CHOICES):
            return Response(
                {'error': '无效的状态值'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 记录原状态
        old_status = step.status
        
        # 更新状态
        step.status = new_status
        
        # 如果是完成状态，自动设置结束时间
        if new_status == 'completed' and not step.end_time:
            step.end_time = datetime.now()
            
        step.save()
        
        return Response({
            'status': 'success',
            'old_status': old_status,
            'new_status': new_status,
            'end_time': step.end_time
        })


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
    def step_statistics(self, request):
        """获取按生产步骤统计的数据"""
        # 获取查询参数
        status = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        category = request.query_params.get('category')

        # 构建基础查询
        orders = ProductionOrder.objects.all()

        # 应用日期过滤
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                orders = orders.filter(created_at__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                orders = orders.filter(created_at__lte=end_date)
            except ValueError:
                pass
            
        # 应用类目过滤
        if category:
            orders = orders.filter(category_id=category)

        # 获取总订单数
        total_orders = orders.count()

        # 存储每个订单的当前步骤
        order_current_steps = {}
        
        # 遍历所有订单获取当前步骤
        for order in orders:
            # 首先查找进行中的步骤
            current_step = ProductionStep.objects.filter(
                order=order,
                status='in_progress'
            ).order_by('sequence').first()
            
            # 如果没有进行中的步骤，查找待处理的步骤
            if not current_step:
                current_step = ProductionStep.objects.filter(
                    order=order,
                    status='pending'
                ).order_by('sequence').first()
            
            if current_step:
                order_current_steps[order.id] = current_step.step_name

        # 统计每个步骤的订单数量
        step_counts = {}
        for step_name in dict(ProductionStep.STEP_NAME_CHOICES).keys():
            count = sum(1 for step in order_current_steps.values() if step == step_name)
            if count > 0:  # 只包含有订单的步骤
                step_counts[step_name] = count

        # 格式化数据
        formatted_data = []
        for step_name, count in step_counts.items():
            step_name_display = dict(ProductionStep.STEP_NAME_CHOICES).get(step_name, step_name)
            percentage = round((count / total_orders * 100), 1) if total_orders > 0 else 0
            
            # 获取该步骤的状态分布
            status_distribution = ProductionStep.objects.filter(
                order__in=orders,
                step_name=step_name
            ).values('status').annotate(
                count=Count('id')
            )

            status_counts = {
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'on_hold': 0
            }
            for item in status_distribution:
                status_counts[item['status']] = item['count']
            
            formatted_data.append({
                'step_name': step_name_display,
                'count': count,
                'percentage': percentage,
                'status_distribution': status_counts
            })

        # 按数量降序排序
        formatted_data.sort(key=lambda x: x['count'], reverse=True)

        return Response({
            'data': formatted_data,
            'total': total_orders
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

    @action(detail=False, methods=['get'])
    def category_priority_statistics(self, request):
        """获取各类目下不同优先级的任务数统计"""
        # 获取查询参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status = request.query_params.get('status')

        # 构建基础查询
        orders = ProductionOrder.objects.all()

        # 应用日期过滤
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                orders = orders.filter(created_at__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                orders = orders.filter(created_at__lte=end_date)
            except ValueError:
                pass

        # 应用状态过滤
        if status:
            orders = orders.filter(status=status)

        # 获取所有活跃的类目
        categories = ProductionCategory.objects.filter(is_active=True)
        
        # 打印调试信息
        print("Total orders:", orders.count())
        print("Total categories:", categories.count())
        
        # 按类目和优先级分组统计
        priority_stats = orders.values(
            'category_id',
            'category__name',
            'priority'
        ).annotate(
            count=Count('id')
        ).order_by('category_id', 'priority')
        
        # 打印原始统计数据
        print("Raw priority stats:", list(priority_stats))

        # 将统计数据转换为字典格式，方便查找
        stats_dict = {}
        for stat in priority_stats:
            category_id = stat['category_id']
            if category_id not in stats_dict:
                stats_dict[category_id] = {
                    'name': stat['category__name'],
                    'priorities': {}
                }
            stats_dict[category_id]['priorities'][stat['priority']] = stat['count']
        
        # 打印处理后的统计字典
        print("Processed stats dict:", stats_dict)

        # 优先级映射关系
        priority_mapping = {
            0: 'P0',
            1: 'P1',
            2: 'P2',
            3: 'P3'
        }

        # 格式化数据
        formatted_data = []
        for category in categories:
            # 初始化优先级分布
            priority_distribution = {
                'P0': 0,
                'P1': 0,
                'P2': 0,
                'P3': 0
            }
            
            # 如果该类目有统计数据，更新优先级分布
            if category.id in stats_dict:
                category_stats = stats_dict[category.id]['priorities']
                for priority_num, count in category_stats.items():
                    priority_key = priority_mapping.get(priority_num, 'P0')  # 默认为 P0
                    priority_distribution[priority_key] = count

            # 只有当类目有任务时才添加到结果中
            if any(count > 0 for count in priority_distribution.values()):
                formatted_data.append({
                    'category_name': category.name,
                    'priority_distribution': priority_distribution
                })

        # 按类目名称排序
        formatted_data.sort(key=lambda x: x['category_name'])
        
        # 打印最终格式化数据
        print("Final formatted data:", formatted_data)

        return Response({
            'data': formatted_data
        })

    @action(detail=False, methods=['get'])
    def channel_statistics(self, request):
        """获取各渠道任务数量统计"""
        try:
            # 获取查询参数
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            status = request.query_params.get('status')

            # 构建基础查询
            orders = ProductionOrder.objects.all()
            
            print("Initial orders count:", orders.count())  # 调试日志

            # 应用日期过滤
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    orders = orders.filter(created_at__gte=start_date)
                    print(f"After start_date filter ({start_date}), orders count:", orders.count())
                except ValueError as e:
                    print(f"Invalid start_date format: {e}")
                    return Response(
                        {'error': f'无效的开始日期格式: {start_date}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    orders = orders.filter(created_at__lte=end_date)
                    print(f"After end_date filter ({end_date}), orders count:", orders.count())
                except ValueError as e:
                    print(f"Invalid end_date format: {e}")
                    return Response(
                        {'error': f'无效的结束日期格式: {end_date}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 应用状态过滤
            if status:
                orders = orders.filter(status=status)
                print(f"After status filter ({status}), orders count:", orders.count())

            # 获取总任务数
            total_orders = orders.count()
            print("Total orders for statistics:", total_orders)

            # 按渠道分组统计任务数
            channel_stats = orders.values(
                'channel',  # 添加channel ID
                'channel__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            print("Raw channel stats:", list(channel_stats))  # 调试日志

            # 格式化数据
            formatted_data = []
            for stat in channel_stats:
                channel_name = stat['channel__name'] or '未分类'
                count = stat['count']
                percentage = round((count / total_orders * 100), 1) if total_orders > 0 else 0
                
                formatted_data.append({
                    'channel_name': channel_name,
                    'count': count,
                    'percentage': percentage
                })
            
            print("Formatted data:", formatted_data)  # 调试日志

            return Response({
                'data': formatted_data,
                'total': total_orders
            })
            
        except Exception as e:
            print(f"Error in channel_statistics: {str(e)}")  # 错误日志
            return Response(
                {'error': f'获取渠道统计数据时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 