from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.authentication.serializers import UserSerializer
from apps.products.serializers import ProductSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    class Meta:
        model = Supplier
        fields = '__all__'


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """采购订单明细序列化器"""
    product_info = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'product', 'product_info',
            'quantity', 'unit_price', 'total_price',
            'received_quantity', 'remark',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_price']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """采购订单序列化器"""
    supplier_info = SupplierSerializer(source='supplier', read_only=True)
    purchaser_info = UserSerializer(source='purchaser', read_only=True)
    items = PurchaseOrderItemSerializer(source='purchaseorderitem_set', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'order_time',
            'supplier', 'supplier_info',
            'purchaser', 'purchaser_info',
            'warehouse_id', 'status', 'status_display',
            'total_amount', 'expected_delivery_date',
            'actual_delivery_date', 'tracking_number',
            'remark', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_amount']

    def validate_expected_delivery_date(self, value):
        """验证预计交付日期"""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("预计交付日期不能早于今天")
        return value

    def validate(self, data):
        """验证订单数据"""
        if data.get('actual_delivery_date'):
            if data['actual_delivery_date'] < data.get('expected_delivery_date'):
                raise serializers.ValidationError({
                    'actual_delivery_date': '实际交付日期不能早于预计交付日期'
                })
        return data 