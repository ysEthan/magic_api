from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.db.models import F
from django.db import connection
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from .serializers import (
    SupplierSerializer, PurchaseOrderSerializer,
    PurchaseOrderItemSerializer
)
from datetime import datetime


class SupplierFilter(filters.FilterSet):
    """供应商过滤器"""
    class Meta:
        model = Supplier
        fields = {
            'status': ['exact'],
            'name': ['icontains'],
            'contact_person': ['icontains'],
            'contact_phone': ['icontains'],
        }


class SupplierViewSet(viewsets.ModelViewSet):
    """供应商视图集"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SupplierFilter
    search_fields = ['name', 'contact_person', 'contact_phone', 'address']
    ordering_fields = ['created_at', 'name']


class PurchaseOrderFilter(filters.FilterSet):
    """采购订单过滤器"""
    min_order_time = filters.DateTimeFilter(field_name='order_time', lookup_expr='gte')
    max_order_time = filters.DateTimeFilter(field_name='order_time', lookup_expr='lte')
    min_total_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_total_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')

    class Meta:
        model = PurchaseOrder
        fields = {
            'status': ['exact'],
            'supplier': ['exact'],
            'purchaser': ['exact'],
            'warehouse_id': ['exact'],
        }


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """采购订单视图集"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PurchaseOrderFilter
    search_fields = ['order_number', 'remark']
    ordering_fields = ['created_at', 'order_time', 'total_amount']

    def perform_create(self, serializer):
        """创建时设置采购员为当前用户"""
        serializer.save(purchaser=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新订单状态"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(PurchaseOrder.ORDER_STATUS_CHOICES):
            return Response(
                {'error': '无效的状态值'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 状态变更时的特殊处理
        if new_status == 'submitted':
            order.order_time = datetime.now()
        elif new_status == 'completed':
            if not order.actual_delivery_date:
                order.actual_delivery_date = datetime.now().date()

        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class LargeResultsSetPagination(PageNumberPagination):
    """大数据集分页器"""
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """采购订单明细视图集"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['purchase_order', 'product']
    search_fields = ['remark']
    ordering_fields = ['created_at', 'quantity', 'unit_price', 'total_price']
    pagination_class = LargeResultsSetPagination  # 使用自定义分页器

    def get_queryset(self):
        """可以通过订单ID过滤明细"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(purchase_order_id=order_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='pending-storage', url_name='pending-storage')
    def pending_storage(self, request):
        """获取待入库的采购订单明细列表"""
        # 1. 首先获取待入库状态的订单
        pending_orders = PurchaseOrder.objects.filter(status='pending_storage')
        
        # 2. 基于这些订单获取订单明细
        queryset = self.get_queryset().filter(
            purchase_order__in=pending_orders,
            received_quantity__lt=F('quantity')
        ).annotate(
            pending_quantity=F('quantity') - F('received_quantity'),
            supplier_id=F('purchase_order__supplier__id'),
            supplier_name=F('purchase_order__supplier__name'),
            order_number=F('purchase_order__order_number'),
            expected_date=F('purchase_order__expected_delivery_date')
        ).select_related(
            'purchase_order',
            'purchase_order__supplier',
            'product'
        )

        # 应用过滤
        order_number = request.query_params.get('order_number')
        if order_number:
            queryset = queryset.filter(purchase_order__order_number__icontains=order_number)
        
        supplier = request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(purchase_order__supplier__id=supplier)
        
        supplier_name = request.query_params.get('supplier_name')
        if supplier_name:
            queryset = queryset.filter(purchase_order__supplier__name__icontains=supplier_name)
        
        product = request.query_params.get('product')
        if product:
            queryset = queryset.filter(product__id=product)
        
        product_name = request.query_params.get('product_name')
        if product_name:
            queryset = queryset.filter(product__name__icontains=product_name)
        
        sku = request.query_params.get('sku')
        if sku:
            queryset = queryset.filter(product__sku__icontains=sku)
        
        expected_date_start = request.query_params.get('expected_date_start')
        if expected_date_start:
            queryset = queryset.filter(purchase_order__expected_delivery_date__gte=expected_date_start)
        
        expected_date_end = request.query_params.get('expected_date_end')
        if expected_date_end:
            queryset = queryset.filter(purchase_order__expected_delivery_date__lte=expected_date_end)

        # 排序
        ordering = request.query_params.get('ordering', '-expected_date')
        if ordering:
            queryset = queryset.order_by(ordering)

        # 打印SQL查询
        queries = connection.queries
        print("SQL查询:")
        for query in queries:
            print(query['sql'])
        print(f"查询结果数量: {queryset.count()}")

        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data) 