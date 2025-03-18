from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as filters
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
from datetime import datetime
from .models import Brand, Category, SPU, Product
from .serializers import (
    BrandSerializer, CategorySerializer, SPUSerializer, ProductSerializer
)
from django.conf import settings

logger = logging.getLogger('django')


class BrandViewSet(viewsets.ModelViewSet):
    """品牌管理视图集"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']


class CategoryViewSet(viewsets.ModelViewSet):
    """商品分类视图集"""
    queryset = Category.objects.filter(parent=None)  # 只获取顶级分类
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['level', 'is_active']
    search_fields = ['name', 'name_en']

    @action(detail=False, methods=['get'])
    def all_categories(self, request):
        """获取所有分类的平铺列表"""
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class SPUFilter(filters.FilterSet):
    """SPU过滤器"""
    min_created_at = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    max_created_at = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = SPU
        fields = {
            'product_type': ['exact'],
            'production_process': ['exact'],
            'brand': ['exact'],
            'category': ['exact'],
            'is_active': ['exact'],
            'poc': ['exact'],
        }


class SPUViewSet(viewsets.ModelViewSet):
    """SPU管理视图集"""
    queryset = SPU.objects.all()
    serializer_class = SPUSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SPUFilter
    search_fields = ['code', 'name', 'remark']
    ordering_fields = ['created_at', 'updated_at']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换SPU的启用状态"""
        spu = self.get_object()
        spu.is_active = not spu.is_active
        spu.save()
        return Response({'status': 'success', 'is_active': spu.is_active})


class ProductFilter(filters.FilterSet):
    """SKU过滤器"""
    min_weight = filters.NumberFilter(field_name='weight', lookup_expr='gte')
    max_weight = filters.NumberFilter(field_name='weight', lookup_expr='lte')

    class Meta:
        model = Product
        fields = {
            'spu': ['exact'],
            'material': ['exact'],
            'color': ['exact'],
            'plating_process': ['exact'],
            'is_reviewed': ['exact'],
            'is_active': ['exact'],
        }


class ProductViewSet(viewsets.ModelViewSet):
    """SKU管理视图集"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProductFilter
    search_fields = ['code', 'name', 'material', 'color']
    ordering_fields = ['created_at', 'updated_at', 'weight']

    @action(detail=True, methods=['post'])
    def toggle_review(self, request, pk=None):
        """切换SKU的审核状态"""
        product = self.get_object()
        product.is_reviewed = not product.is_reviewed
        product.save()
        return Response({'status': 'success', 'is_reviewed': product.is_reviewed})

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny],
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request):
        """上传商品图片（无需认证）"""
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response(
                    {'error': '没有提供图片文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if image_file.content_type not in allowed_types:
                return Response(
                    {'error': '不支持的文件类型，仅支持JPG、PNG和GIF'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证文件大小（最大5MB）
            if image_file.size > 5 * 1024 * 1024:
                return Response(
                    {'error': '文件大小超过限制（最大5MB）'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 使用原始文件名保存到products目录
            logger.info("=== Image Upload Info ===")
            logger.info(f"Original filename: {image_file.name}")
            path = default_storage.save(image_file.name, ContentFile(image_file.read()))
            logger.info(f"Saved path: {path}")
            image_url = default_storage.url(path)
            logger.info(f"Image URL: {image_url}")
            logger.info(f"Full file path: {os.path.join(settings.MEDIA_ROOT, path)}")
            logger.info("==========================")

            return Response({
                'message': '图片上传成功',
                'image_url': image_url
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'图片上传失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 