from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as df_filters
from django.utils import timezone
from django.db.models import Q
from .models import Shop, Order, OrderItem
from .serializers import (
    ShopSerializer, OrderSerializer, OrderItemSerializer,
    OrderCreateSerializer
)

class ShopFilter(df_filters.FilterSet):
    """店铺过滤器"""
    name = df_filters.CharFilter(lookup_expr='icontains')
    platform = df_filters.ChoiceFilter(choices=Shop.PLATFORM_CHOICES)
    status = df_filters.ChoiceFilter(choices=Shop.STATUS_CHOICES)
    created_at = df_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Shop
        fields = ['name', 'platform', 'status', 'created_at']

class ShopViewSet(viewsets.ModelViewSet):
    """店铺视图集"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    filterset_class = ShopFilter
    search_fields = ['name', 'shop_code', 'description']
    ordering_fields = ['created_at', 'platform', 'name']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换店铺状态"""
        shop = self.get_object()
        shop.status = 0 if shop.status == 1 else 1
        shop.save()
        return Response({
            'status': shop.status,
            'message': '店铺状态已更新'
        })

class OrderFilter(df_filters.FilterSet):
    """订单过滤器"""
    order_number = df_filters.CharFilter(lookup_expr='icontains')
    platform_order_number = df_filters.CharFilter(lookup_expr='icontains')
    status = df_filters.ChoiceFilter(choices=Order.ORDER_STATUS_CHOICES)
    order_type = df_filters.ChoiceFilter(choices=Order.ORDER_TYPE_CHOICES)
    shop = df_filters.NumberFilter()
    payment_status = df_filters.BooleanFilter()
    created_at = df_filters.DateTimeFromToRangeFilter()
    order_place_time = df_filters.DateTimeFromToRangeFilter()
    payment_time = df_filters.DateTimeFromToRangeFilter()
    total_amount = df_filters.RangeFilter()
    shipping_contact = df_filters.CharFilter(lookup_expr='icontains')
    shipping_phone = df_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Order
        fields = [
            'order_number', 'platform_order_number', 'status', 'order_type',
            'shop', 'payment_status', 'created_at', 'order_place_time',
            'payment_time', 'total_amount', 'shipping_contact', 'shipping_phone'
        ]

class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    queryset = Order.objects.all()
    filterset_class = OrderFilter
    search_fields = [
        'order_number', 'platform_order_number', 'shipping_contact',
        'shipping_phone', 'shipping_address'
    ]
    ordering_fields = [
        'created_at', 'order_place_time', 'payment_time',
        'total_amount', 'status'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        # 添加商品关联查询，减少数据库查询次数
        return queryset.select_related('shop').prefetch_related('items', 'items__product')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新订单状态"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return Response({
                'error': '无效的订单状态'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 更新订单状态
        order.status = new_status
        # 如果订单状态变更为已支付，更新支付状态和时间
        if new_status == 'paid':
            order.payment_status = True
            order.payment_time = timezone.now()
        order.save()

        return Response({
            'status': order.status,
            'message': '订单状态已更新'
        })

    @action(detail=True, methods=['post'])
    def update_payment(self, request, pk=None):
        """更新支付状态"""
        order = self.get_object()
        payment_status = request.data.get('payment_status', False)
        
        order.payment_status = payment_status
        if payment_status:
            order.payment_time = timezone.now()
        order.save()

        return Response({
            'payment_status': order.payment_status,
            'payment_time': order.payment_time,
            'message': '支付状态已更新'
        })

class OrderItemViewSet(viewsets.ModelViewSet):
    """订单商品视图集"""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filterset_fields = ['order', 'product']
    search_fields = ['remark']
    ordering_fields = ['created_at', 'quantity', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        # 添加订单和商品关联查询，减少数据库查询次数
        return queryset.select_related('order', 'product') 