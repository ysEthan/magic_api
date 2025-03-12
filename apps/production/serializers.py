from rest_framework import serializers
from .models import ProductionCategory, ProductionOrder, ProductionStep, ProductionComment, ProductionChannel
from apps.authentication.serializers import UserSerializer
from django.conf import settings
from datetime import datetime


class ProductionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCategory
        fields = '__all__'


class ProductionStepSerializer(serializers.ModelSerializer):
    step_name_display = serializers.CharField(source='get_step_name_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_info = UserSerializer(source='operator', read_only=True)

    class Meta:
        model = ProductionStep
        fields = '__all__'

    def validate(self, data):
        """验证步骤数据"""
        # 验证序号是否重复
        if self.instance is None:  # 创建新步骤时
            order = data.get('order')
            sequence = data.get('sequence')
            if ProductionStep.objects.filter(
                order=order, 
                sequence=sequence
            ).exists():
                raise serializers.ValidationError({
                    'sequence': '该序号在当前任务中已存在'
                })
        
        # 验证开始时间小于结束时间
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError({
                'end_time': '结束时间不能早于开始时间'
            })
            
        return data


class ProductionCommentSerializer(serializers.ModelSerializer):
    author_info = UserSerializer(source='author', read_only=True)
    replies = serializers.SerializerMethodField()
    comment_type_display = serializers.CharField(source='get_comment_type_display', read_only=True)

    class Meta:
        model = ProductionComment
        fields = '__all__'

    def get_replies(self, obj):
        if obj.replies.exists():
            return ProductionCommentSerializer(obj.replies.all(), many=True).data
        return []


class ProductionChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionChannel
        fields = ['id', 'code', 'name', 'description', 'is_active']


class ProductionOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    manager_info = UserSerializer(source='manager', read_only=True)
    created_by_info = UserSerializer(source='created_by', read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    steps = ProductionStepSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField(read_only=True)
    category_info = serializers.SerializerMethodField(read_only=True)
    main_image_url = serializers.SerializerMethodField(read_only=True)
    channel_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductionOrder
        fields = '__all__'
        extra_kwargs = {
            'product': {'required': False, 'allow_null': True},
            'category': {'required': False, 'allow_null': True},
            'priority_order': {'required': False},
            'main_image': {'required': False},
            'attachments': {'required': False}
        }

    def get_comments(self, obj):
        return ProductionCommentSerializer(
            obj.comments.filter(parent=None), 
            many=True
        ).data

    def get_product_info(self, obj):
        if obj.product:
            return {
                'id': obj.product.id,
                'code': obj.product.code,
                'name': obj.product.name
            }
        return None

    def get_category_info(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'code': obj.category.code,
                'name': obj.category.name,
                'category_type': obj.category.category_type,
                'category_type_display': obj.category.get_category_type_display()
            }
        return None

    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None

    def get_channel_info(self, obj):
        if obj.channel:
            return {
                'id': obj.channel.id,
                'code': obj.channel.code,
                'name': obj.channel.name
            }
        return None

    def validate_attachments(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('附件必须是URL列表格式')
        return value

    def validate_main_image(self, value):
        if value:
            if value.size > settings.MAX_UPLOAD_SIZE:
                raise serializers.ValidationError('图片大小超过限制')
            if value.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise serializers.ValidationError('不支持的图片格式')
        return value

    def validate(self, data):
        if data.get('category') and not data['category'].is_active:
            raise serializers.ValidationError({
                'category': '所选类目未启用'
            })
        
        if 'priority_order' in data and data['priority_order'] < 0:
            raise serializers.ValidationError({
                'priority_order': '优先级排序值不能小于0'
            })
            
        return data

    def validate_code(self, value):
        """不再验证编号格式"""
        return value

    def create(self, validated_data):
        """如果没有提供编号，自动生成"""
        if 'code' not in validated_data:
            validated_data['code'] = ProductionOrder.generate_next_code()
        return super().create(validated_data) 