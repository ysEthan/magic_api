from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from apps.products.models import Product

User = get_user_model()

class ProductionCategory(models.Model):
    """生产类目"""
    CATEGORY_CHOICES = (
        ('resin', '树脂类'),
        ('metal', '金属类'),
        ('ceramic', '陶瓷类'),
        ('plush', '毛绒类'),
    )

    code = models.CharField(_('类目编码'), max_length=20, unique=True)
    name = models.CharField(_('类目名称'), max_length=50)
    category_type = models.CharField(
        _('类目类型'),
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField(_('类目描述'), blank=True)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('生产类目')
        verbose_name_plural = _('生产类目')
        ordering = ['code']

    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class ProductionOrder(models.Model):
    """生产任务订单"""
    ORDER_TYPE_CHOICES = (
        ('trial', '试产'),
        ('mass', '量产'),
    )
    
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    PRIORITY_CHOICES = (
        (0, '紧急'),
        (1, '高'),
        (2, '中'),
        (3, '低'),
    )

    code = models.CharField(_('任务编号'), max_length=50, unique=True)
    product = models.ForeignKey(
        Product,
        verbose_name=_('产品'),
        on_delete=models.PROTECT,
        related_name='production_orders',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        ProductionCategory,
        verbose_name=_('生产类目'),
        on_delete=models.PROTECT,
        related_name='orders',
        null=True,
        blank=True
    )
    order_type = models.CharField(
        _('生产类型'),
        max_length=10,
        choices=ORDER_TYPE_CHOICES
    )
    quantity = models.IntegerField(_('计划数量'), validators=[MinValueValidator(1)])
    priority = models.IntegerField(
        _('优先级'),
        choices=PRIORITY_CHOICES,
        default=2
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    planned_start_date = models.DateField(_('计划开始日期'))
    planned_end_date = models.DateField(_('计划结束日期'))
    actual_start_date = models.DateField(_('实际开始日期'), null=True, blank=True)
    actual_end_date = models.DateField(_('实际结束日期'), null=True, blank=True)
    manager = models.ForeignKey(
        User,
        verbose_name=_('生产主管'),
        on_delete=models.PROTECT,
        related_name='managed_orders'
    )
    description = models.TextField(_('任务描述'), blank=True)
    technical_requirements = models.TextField(_('技术要求'), blank=True)
    quality_requirements = models.TextField(_('质量要求'), blank=True)
    created_by = models.ForeignKey(
        User,
        verbose_name=_('创建人'),
        on_delete=models.PROTECT,
        related_name='created_orders'
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('生产任务')
        verbose_name_plural = _('生产任务')
        ordering = ['-created_at']

    def __str__(self):
        product_name = self.product.name if self.product else "未关联产品"
        return f"{self.code} - {product_name}"


class ProductionStep(models.Model):
    """生产步骤"""
    STEP_CHOICES = (
        ('3d_modeling', '3D建模'),
        ('model_printing', '模型打印'),
        ('casting', '铸造'),
        ('plating', '电镀'),
        ('post_processing', '后处理'),
    )

    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('on_hold', '已暂停'),
    )

    order = models.ForeignKey(
        ProductionOrder,
        verbose_name=_('生产任务'),
        on_delete=models.CASCADE,
        related_name='steps'
    )
    step_type = models.CharField(
        _('步骤类型'),
        max_length=20,
        choices=STEP_CHOICES
    )
    name = models.CharField(
        _('步骤名称'),
        max_length=100,
        help_text=_('可以是预定义步骤，也可以是自定义步骤名称')
    )
    sequence = models.IntegerField(_('步骤顺序'))
    description = models.TextField(_('步骤描述'), blank=True)
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    planned_duration = models.DurationField(_('计划耗时'))
    actual_duration = models.DurationField(_('实际耗时'), null=True, blank=True)
    start_time = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    operator = models.ForeignKey(
        User,
        verbose_name=_('操作员'),
        on_delete=models.PROTECT,
        related_name='operated_steps'
    )
    quality_check_result = models.TextField(_('质检结果'), blank=True)
    notes = models.TextField(_('备注'), blank=True)
    attachments = models.JSONField(
        _('附件列表'),
        default=list,
        blank=True,
        help_text=_('步骤相关的文件URL列表，如3D文件、图纸等')
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('生产步骤')
        verbose_name_plural = _('生产步骤')
        ordering = ['order', 'sequence']
        unique_together = ['order', 'sequence']

    def __str__(self):
        return f"{self.order.code} - {self.get_step_type_display() or self.name}"

    def save(self, *args, **kwargs):
        if self.step_type and not self.name:
            self.name = self.get_step_type_display()
        super().save(*args, **kwargs)


class ProductionComment(models.Model):
    """生产评论"""
    COMMENT_TYPE_CHOICES = (
        ('general', '普通评论'),
        ('issue', '问题报告'),
        ('solution', '解决方案'),
    )

    order = models.ForeignKey(
        ProductionOrder,
        verbose_name=_('生产任务'),
        on_delete=models.CASCADE,
        related_name='comments'
    )
    step = models.ForeignKey(
        ProductionStep,
        verbose_name=_('生产步骤'),
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )
    comment_type = models.CharField(
        _('评论类型'),
        max_length=20,
        choices=COMMENT_TYPE_CHOICES,
        default='general'
    )
    content = models.TextField(_('评论内容'))
    images = models.JSONField(
        _('图片列表'),
        default=list,
        blank=True,
        help_text=_('评论相关的图片URL列表')
    )
    author = models.ForeignKey(
        User,
        verbose_name=_('评论人'),
        on_delete=models.PROTECT,
        related_name='production_comments'
    )
    parent = models.ForeignKey(
        'self',
        verbose_name=_('父评论'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('生产评论')
        verbose_name_plural = _('生产评论')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.code} - {self.author.username} - {self.created_at}" 