from rest_framework import serializers
from .models import ProductionCategory, ProductionOrder, ProductionStep, ProductionComment
from apps.authentication.serializers import UserSerializer


class ProductionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCategory
        fields = '__all__'


class ProductionStepSerializer(serializers.ModelSerializer):
    step_type_display = serializers.CharField(source='get_step_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_info = UserSerializer(source='operator', read_only=True)

    class Meta:
        model = ProductionStep
        fields = '__all__'


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


class ProductionOrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    manager_info = UserSerializer(source='manager', read_only=True)
    created_by_info = UserSerializer(source='created_by', read_only=True)
    steps = ProductionStepSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField(read_only=True)
    category_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductionOrder
        fields = '__all__'
        extra_kwargs = {
            'product': {'required': False, 'allow_null': True},
            'category': {'required': False, 'allow_null': True},
            'priority_order': {'required': False}
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