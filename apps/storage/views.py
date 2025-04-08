from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, F
from django_filters import rest_framework as filters
from .models import Warehouse, Inventory, StockIn, StockOut
from .serializers import (
    WarehouseSerializer, InventorySerializer,
    StockInSerializer, StockOutSerializer
)


class WarehouseViewSet(viewsets.ModelViewSet):
    """仓库管理视图集"""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['warehouse_code', 'warehouse_name', 'location', 'contact_phone']
    ordering_fields = ['warehouse_code', 'created_at']

    @action(detail=True, methods=['get'])
    def inventory_summary(self, request, pk=None):
        """获取仓库库存汇总信息"""
        warehouse = self.get_object()
        inventory_data = Inventory.objects.filter(
            warehouse=warehouse
        ).values(
            'product'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('unit_cost'))
        )
        return Response(inventory_data)


class InventoryViewSet(viewsets.ModelViewSet):
    """库存管理视图集"""
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['warehouse', 'product']
    search_fields = ['batch_code']
    ordering_fields = ['created_at', 'quantity']

    @action(detail=False, methods=['get'])
    def product_inventory(self, request):
        """获取商品库存汇总"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {"error": "必须提供product_id参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inventory_data = Inventory.objects.filter(
            product_id=product_id
        ).values(
            'warehouse'
        ).annotate(
            total_quantity=Sum('quantity')
        )
        return Response(inventory_data)


class StockInViewSet(viewsets.ModelViewSet):
    """入库管理视图集"""
    queryset = StockIn.objects.all()
    serializer_class = StockInSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['warehouse', 'product', 'stock_in_type']
    search_fields = ['stock_in_code', 'source_order', 'remark']
    ordering_fields = ['stock_in_time', 'created_at']

    def perform_create(self, serializer):
        """创建入库记录时自动生成批次"""
        # 生成入库单号
        current_date = timezone.now()
        prefix = f"IN{current_date.strftime('%y%m%d')}"
        count = StockIn.objects.filter(
            stock_in_code__startswith=prefix
        ).count()
        stock_in_code = f"{prefix}{str(count + 1).zfill(4)}"
        
        # 生成批次号
        batch_prefix = f"B{current_date.strftime('%y%m%d')}"
        batch_count = Inventory.objects.filter(
            batch_code__startswith=batch_prefix
        ).count()
        batch_code = f"{batch_prefix}{str(batch_count + 1).zfill(4)}"
        
        # 创建库存记录
        inventory = Inventory.objects.create(
            warehouse=serializer.validated_data['warehouse'],
            product=serializer.validated_data['product'],
            batch_code=batch_code,
            quantity=serializer.validated_data['quantity'],
            unit_cost=serializer.validated_data['unit_cost']
        )
        
        # 保存入库记录
        serializer.save(
            stock_in_code=stock_in_code,
            inventory=inventory,
            operator=self.request.user
        )


class StockOutViewSet(viewsets.ModelViewSet):
    """出库管理视图集"""
    queryset = StockOut.objects.all()
    serializer_class = StockOutSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['warehouse', 'product', 'stock_out_type']
    search_fields = ['stock_out_code', 'related_order', 'remark']
    ordering_fields = ['stock_out_time', 'created_at']

    def perform_create(self, serializer):
        """创建出库记录时自动生成出库单号并更新库存"""
        # 生成出库单号
        current_date = timezone.now()
        prefix = f"OUT{current_date.strftime('%y%m%d')}"
        count = StockOut.objects.filter(
            stock_out_code__startswith=prefix
        ).count()
        stock_out_code = f"{prefix}{str(count + 1).zfill(4)}"
        
        # 检查并更新库存
        inventory = serializer.validated_data['inventory']
        quantity = serializer.validated_data['quantity']
        
        if inventory.quantity < quantity:
            raise serializers.ValidationError({
                "quantity": f"库存不足，当前库存: {inventory.quantity}"
            })
        
        inventory.quantity -= quantity
        inventory.save()
        
        # 保存出库记录
        serializer.save(
            stock_out_code=stock_out_code,
            operator=self.request.user
        ) 