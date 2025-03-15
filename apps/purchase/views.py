from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
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


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """采购订单明细视图集"""
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['purchase_order', 'product']
    search_fields = ['remark']
    ordering_fields = ['created_at', 'quantity', 'unit_price', 'total_price']

    def get_queryset(self):
        """可以通过订单ID过滤明细"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(purchase_order_id=order_id)
        return queryset 