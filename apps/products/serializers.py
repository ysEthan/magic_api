from rest_framework import serializers
from .models import Brand, Category, SPU, Product


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name_en', 'name', 'description', 'parent', 'rank',
                 'level', 'is_last_level', 'is_active', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class SimpleCategorySerializer(serializers.ModelSerializer):
    """简化的分类序列化器，用于SPU中的嵌套"""
    class Meta:
        model = Category
        fields = ['id', 'name_en', 'name', 'level']


class SimpleBrandSerializer(serializers.ModelSerializer):
    """简化的品牌序列化器，用于SPU中的嵌套"""
    class Meta:
        model = Brand
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = Product
        fields = '__all__'


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    brand = SimpleBrandSerializer(read_only=True)
    brand_id = serializers.IntegerField(write_only=True, required=False)
    category = SimpleCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    products = ProductSerializer(many=True, read_only=True)
    poc_name = serializers.CharField(source='poc.username', read_only=True)

    class Meta:
        model = SPU
        fields = ['id', 'code', 'name', 'product_type', 'remark', 'sales_channel',
                 'design_elements', 'production_process', 'brand', 'brand_id',
                 'category', 'category_id', 'poc', 'poc_name', 'is_active',
                 'created_at', 'updated_at', 'products']

    def validate_category_id(self, value):
        try:
            category = Category.objects.get(id=value)
            if not category.is_last_level:
                raise serializers.ValidationError("必须选择最后一级分类")
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("分类不存在") 