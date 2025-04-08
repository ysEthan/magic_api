from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Warehouse, Inventory, StockIn, StockOut
from apps.products.serializers import ProductSerializer

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    manager_info = UserSimpleSerializer(source='manager', read_only=True)

    class Meta:
        model = Warehouse
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器"""
    warehouse_info = WarehouseSerializer(source='warehouse', read_only=True)
    product_info = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'


class StockInSerializer(serializers.ModelSerializer):
    """入库记录序列化器"""
    warehouse_info = WarehouseSerializer(source='warehouse', read_only=True)
    product_info = ProductSerializer(source='product', read_only=True)
    operator_info = UserSimpleSerializer(source='operator', read_only=True)
    stock_in_type_display = serializers.CharField(source='get_stock_in_type_display', read_only=True)

    class Meta:
        model = StockIn
        fields = '__all__'


class StockOutSerializer(serializers.ModelSerializer):
    """出库记录序列化器"""
    warehouse_info = WarehouseSerializer(source='warehouse', read_only=True)
    product_info = ProductSerializer(source='product', read_only=True)
    operator_info = UserSimpleSerializer(source='operator', read_only=True)
    stock_out_type_display = serializers.CharField(source='get_stock_out_type_display', read_only=True)

    class Meta:
        model = StockOut
        fields = '__all__' 