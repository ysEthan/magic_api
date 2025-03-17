from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Carrier, Service, Package, Tracking
from .serializers import (
    CarrierSerializer, ServiceSerializer,
    PackageSerializer, TrackingSerializer
)


class CarrierFilter(filters.FilterSet):
    """物流商过滤器"""
    name = filters.CharFilter(field_name='name_zh', lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    contact = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Carrier
        fields = ['name', 'code', 'contact']


class CarrierViewSet(viewsets.ModelViewSet):
    """物流商视图集"""
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CarrierFilter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name_zh', 'name_en', 'code', 'contact']
    ordering_fields = ['name_zh', 'code', 'created_at']
    ordering = ['name_zh']


class ServiceFilter(filters.FilterSet):
    """物流服务过滤器"""
    carrier = filters.NumberFilter()
    carrier_name = filters.CharFilter(field_name='carrier__name_zh', lookup_expr='icontains')
    service_name = filters.CharFilter(lookup_expr='icontains')
    service_code = filters.CharFilter(lookup_expr='icontains')
    service_type = filters.NumberFilter()
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Service
        fields = ['carrier', 'carrier_name', 'service_name', 'service_code', 'service_type']


class ServiceViewSet(viewsets.ModelViewSet):
    """物流服务视图集"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ServiceFilter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['service_name', 'service_code', 'carrier__name_zh']
    ordering_fields = ['carrier__name_zh', 'service_name', 'created_at']
    ordering = ['carrier__name_zh', 'service_name']


class PackageFilter(filters.FilterSet):
    """包裹过滤器"""
    order = filters.NumberFilter()
    order_number = filters.CharFilter(field_name='order__order_number', lookup_expr='icontains')
    warehouse = filters.NumberFilter()
    warehouse_name = filters.CharFilter(field_name='warehouse__name', lookup_expr='icontains')
    tracking_no = filters.CharFilter(lookup_expr='icontains')
    pkg_status_code = filters.CharFilter()
    service = filters.NumberFilter()
    carrier = filters.NumberFilter(field_name='service__carrier')
    carrier_name = filters.CharFilter(field_name='service__carrier__name_zh', lookup_expr='icontains')
    created_at = filters.DateTimeFromToRangeFilter()
    estimated_cost_min = filters.NumberFilter(field_name='estimated_logistics_cost', lookup_expr='gte')
    estimated_cost_max = filters.NumberFilter(field_name='estimated_logistics_cost', lookup_expr='lte')

    class Meta:
        model = Package
        fields = [
            'order', 'order_number', 'warehouse', 'warehouse_name',
            'tracking_no', 'pkg_status_code', 'service', 'carrier',
            'carrier_name'
        ]


class PackageViewSet(viewsets.ModelViewSet):
    """包裹视图集"""
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PackageFilter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['tracking_no', 'order__order_number']
    ordering_fields = ['created_at', 'estimated_logistics_cost']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新包裹状态"""
        package = self.get_object()
        new_status = request.data.get('status')
        description = request.data.get('description', '')
        location = request.data.get('location', '')

        if not new_status:
            return Response(
                {'error': _('状态不能为空')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证状态转换的合法性
        valid_transitions = {
            '0': ['1', '4'],  # 待发货 -> 待揽收/已取消
            '1': ['2', '4'],  # 待揽收 -> 转运中/已取消
            '2': ['3', '4'],  # 转运中 -> 已签收/已取消
            '3': [],          # 已签收 -> 不可变更
            '4': [],          # 已取消 -> 不可变更
        }

        if new_status not in valid_transitions.get(package.pkg_status_code, []):
            return Response(
                {'error': _('不允许的状态变更')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建物流轨迹记录
        tracking_data = {
            'package': package,
            'status': int(new_status),
            'location': location,
            'description': description,
            'tracking_time': timezone.now(),
            'operator': request.user
        }
        Tracking.objects.create(**tracking_data)

        # 更新包裹状态
        package.pkg_status_code = new_status
        package.save()

        return Response(self.get_serializer(package).data)


class TrackingFilter(filters.FilterSet):
    """物流轨迹过滤器"""
    package = filters.NumberFilter()
    tracking_no = filters.CharFilter(field_name='package__tracking_no', lookup_expr='icontains')
    status = filters.NumberFilter()
    location = filters.CharFilter(lookup_expr='icontains')
    operator = filters.NumberFilter()
    operator_name = filters.CharFilter(field_name='operator__username', lookup_expr='icontains')
    tracking_time = filters.DateTimeFromToRangeFilter()
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Tracking
        fields = ['package', 'tracking_no', 'status', 'location', 'operator', 'operator_name']


class TrackingViewSet(viewsets.ModelViewSet):
    """物流轨迹视图集"""
    queryset = Tracking.objects.all()
    serializer_class = TrackingSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TrackingFilter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['location', 'description', 'package__tracking_no']
    ordering_fields = ['tracking_time', 'created_at']
    ordering = ['-tracking_time']

    def get_queryset(self):
        """根据包裹ID过滤轨迹记录"""
        queryset = super().get_queryset()
        package_id = self.request.query_params.get('package_id', None)
        if package_id is not None:
            queryset = queryset.filter(package_id=package_id)
        return queryset 