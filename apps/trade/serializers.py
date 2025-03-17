from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.products.serializers import ProductSerializer
from .models import Shop, Order, OrderItem

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ShopSerializer(serializers.ModelSerializer):
    """店铺序列化器"""
    manager_info = UserSerializer(source='manager', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'platform', 'platform_display', 'shop_code',
            'manager', 'manager_info', 'status', 'status_display',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    product_info = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_info', 'quantity',
            'unit_price', 'discount', 'total_price', 'remark',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_price', 'created_at', 'updated_at']

    def validate(self, data):
        """验证数据"""
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError("商品数量必须大于0")
        if data.get('unit_price', 0) < 0:
            raise serializers.ValidationError("商品单价不能为负数")
        if data.get('discount', 0) < 0 or data.get('discount', 0) > 100:
            raise serializers.ValidationError("折扣必须在0-100之间")
        return data

class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    shop_info = ShopSerializer(source='shop', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'platform_order_number', 'order_type',
            'order_type_display', 'exchange_rate_to_usd', 'package_id',
            'shop', 'shop_info', 'status', 'status_display', 'total_amount',
            'currency', 'shipping_fee', 'payment_method', 'payment_method_display',
            'payment_status', 'payment_time', 'order_place_time',
            'shipping_address', 'shipping_contact', 'shipping_phone',
            'postal_code', 'country', 'state', 'city', 'district',
            'system_remark', 'cs_remark', 'buyer_remark', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """验证数据"""
        if data.get('total_amount', 0) < 0:
            raise serializers.ValidationError("订单总金额不能为负数")
        if data.get('shipping_fee', 0) < 0:
            raise serializers.ValidationError("运费不能为负数")
        if data.get('exchange_rate_to_usd', 0) <= 0:
            raise serializers.ValidationError("汇率必须大于0")
        return data

class OrderCreateSerializer(OrderSerializer):
    """创建订单的序列化器"""
    items = OrderItemSerializer(many=True)

    def create(self, validated_data):
        """创建订单及其商品明细"""
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order

    def update(self, instance, validated_data):
        """更新订单及其商品明细"""
        items_data = validated_data.pop('items', [])
        # 更新订单基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新订单商品
        if items_data:
            # 删除原有的商品明细
            instance.items.all().delete()
            # 创建新的商品明细
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance 