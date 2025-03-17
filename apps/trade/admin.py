from django.contrib import admin
from .models import Shop, Order, OrderItem

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'shop_code', 'manager', 'status', 'created_at']
    list_filter = ['platform', 'status', 'created_at']
    search_fields = ['name', 'shop_code', 'description']
    ordering = ['-created_at']
    raw_id_fields = ['manager']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'platform_order_number', 'order_type', 'shop',
        'status', 'total_amount', 'payment_status', 'created_at'
    ]
    list_filter = [
        'status', 'order_type', 'payment_status', 'currency',
        'created_at', 'payment_time'
    ]
    search_fields = [
        'order_number', 'platform_order_number', 'shipping_contact',
        'shipping_phone', 'shipping_address'
    ]
    raw_id_fields = ['shop']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': (
                'order_number', 'platform_order_number', 'order_type',
                'shop', 'status', 'package_id'
            )
        }),
        ('金额信息', {
            'fields': (
                'total_amount', 'currency', 'shipping_fee',
                'exchange_rate_to_usd'
            )
        }),
        ('支付信息', {
            'fields': (
                'payment_method', 'payment_status', 'payment_time',
                'order_place_time'
            )
        }),
        ('收货信息', {
            'fields': (
                'shipping_contact', 'shipping_phone', 'shipping_address',
                'postal_code', 'country', 'state', 'city', 'district'
            )
        }),
        ('备注信息', {
            'fields': (
                'system_remark', 'cs_remark', 'buyer_remark'
            )
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        })
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product', 'quantity', 'unit_price',
        'discount', 'total_price', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product__name', 'remark']
    raw_id_fields = ['order', 'product']
    ordering = ['-created_at']
    readonly_fields = ['total_price', 'created_at', 'updated_at'] 