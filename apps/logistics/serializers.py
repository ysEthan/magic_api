from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Carrier, Service, Package, Tracking


class CarrierSerializer(serializers.ModelSerializer):
    """物流商序列化器"""
    class Meta:
        model = Carrier
        fields = [
            'id', 'name_zh', 'name_en', 'code', 'url', 'contact',
            'query_key', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_code(self, value):
        """验证物流商代码的唯一性"""
        if self.instance is None:  # 创建新记录时
            if Carrier.objects.filter(code=value).exists():
                raise serializers.ValidationError(_('该物流商代码已存在'))
        else:  # 更新记录时
            if Carrier.objects.exclude(id=self.instance.id).filter(code=value).exists():
                raise serializers.ValidationError(_('该物流商代码已存在'))
        return value


class ServiceSerializer(serializers.ModelSerializer):
    """物流服务序列化器"""
    carrier_name = serializers.CharField(source='carrier.name_zh', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'carrier', 'carrier_name', 'service_name',
            'service_code', 'service_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """验证服务代码在同一物流商下的唯一性"""
        carrier = data.get('carrier')
        service_code = data.get('service_code')
        
        if self.instance is None:  # 创建新记录时
            if Service.objects.filter(carrier=carrier, service_code=service_code).exists():
                raise serializers.ValidationError({
                    'service_code': _('该服务代码在当前物流商下已存在')
                })
        else:  # 更新记录时
            if Service.objects.exclude(id=self.instance.id).filter(
                carrier=carrier, service_code=service_code
            ).exists():
                raise serializers.ValidationError({
                    'service_code': _('该服务代码在当前物流商下已存在')
                })
        return data


class TrackingSerializer(serializers.ModelSerializer):
    """物流轨迹序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = Tracking
        fields = [
            'id', 'package', 'status', 'status_display', 'location',
            'description', 'operator', 'operator_name', 'tracking_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'operator']

    def validate_tracking_time(self, value):
        """验证轨迹时间的合理性"""
        if value > self.context['request'].data.get('created_at', value):
            raise serializers.ValidationError(_('轨迹时间不能晚于创建时间'))
        return value

    def create(self, validated_data):
        """创建时自动设置操作人"""
        validated_data['operator'] = self.context['request'].user
        return super().create(validated_data)


class PackageSerializer(serializers.ModelSerializer):
    """包裹序列化器"""
    carrier_name = serializers.CharField(source='carrier_name', read_only=True)
    service_name = serializers.CharField(source='service_name', read_only=True)
    volume = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text=_('体积(cm³)')
    )
    volume_weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text=_('体积重(kg)')
    )
    tracking_records = TrackingSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    order_info = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            'id', 'order', 'order_info', 'warehouse', 'warehouse_name',
            'tracking_no', 'pkg_status_code', 'service', 'carrier_name',
            'service_name', 'items', 'length', 'width', 'height', 'weight',
            'volume', 'volume_weight', 'estimated_logistics_cost',
            'carrier_cost', 'tracking_records', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'carrier_cost',
            'tracking_records'
        ]

    def get_order_info(self, obj):
        """获取订单基本信息"""
        if obj.order:
            return {
                'order_number': obj.order.order_number,
                'shop_name': obj.order.shop.name if obj.order.shop else None,
                'total_amount': str(obj.order.total_amount),
                'status': obj.order.get_status_display(),
            }
        return None

    def validate(self, data):
        """验证包裹数据"""
        # 验证尺寸和重量的合理性
        length = data.get('length')
        width = data.get('width')
        height = data.get('height')
        weight = data.get('weight')

        if any([length, width, height]) and not all([length, width, height]):
            raise serializers.ValidationError(_('包裹的长、宽、高必须同时提供'))

        if any([length, width, height, weight]):
            if length and length <= 0:
                raise serializers.ValidationError({'length': _('长度必须大于0')})
            if width and width <= 0:
                raise serializers.ValidationError({'width': _('宽度必须大于0')})
            if height and height <= 0:
                raise serializers.ValidationError({'height': _('高度必须大于0')})
            if weight and weight <= 0:
                raise serializers.ValidationError({'weight': _('重量必须大于0')})

        # 验证包裹状态变更的合理性
        if self.instance and 'pkg_status_code' in data:
            old_status = self.instance.pkg_status_code
            new_status = data['pkg_status_code']
            
            # 定义状态转换规则
            valid_transitions = {
                '0': ['1', '4'],  # 待发货 -> 待揽收/已取消
                '1': ['2', '4'],  # 待揽收 -> 转运中/已取消
                '2': ['3', '4'],  # 转运中 -> 已签收/已取消
                '3': [],          # 已签收 -> 不可变更
                '4': [],          # 已取消 -> 不可变更
            }
            
            if new_status not in valid_transitions.get(old_status, []):
                raise serializers.ValidationError({
                    'pkg_status_code': _('不允许的状态变更')
                })

        return data 