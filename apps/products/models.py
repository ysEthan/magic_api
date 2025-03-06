from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import os
import uuid

User = get_user_model()

def product_image_path(instance, filename):
    """为商品图片生成上传路径"""
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex[:8]}_{instance.code}.{ext}"
    return os.path.join('products', new_filename)

class Brand(models.Model):
    """品牌"""
    name = models.CharField(_('品牌名称'), max_length=100)
    description = models.TextField(_('品牌描述'), blank=True, null=True)
    logo_url = models.CharField(_('品牌LOGO'), max_length=255, null=True, blank=True)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('品牌')
        verbose_name_plural = _('品牌列表')
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    """商品分类"""
    LEVEL_CHOICES = (
        (1, '一级分类'),
        (2, '二级分类'),
        (3, '三级分类'),
        (4, '四级分类'),
        (5, '五级分类'),
        (6, '六级分类'),
        (7, '七级分类'),
    )

    name_en = models.CharField(_('英文名称'), max_length=100)
    name = models.CharField(_('中文名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        verbose_name=_('父类别'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    rank = models.IntegerField(_('排序'), default=0)
    level = models.IntegerField(
        _('分类层级'),
        choices=LEVEL_CHOICES,
        default=1
    )
    is_last_level = models.BooleanField(_('是否最后一级'), default=False)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商品分类')
        verbose_name_plural = _('商品分类')
        ordering = ['rank', 'id']

    def __str__(self):
        return f"{self.name} ({self.name_en})"

    def clean(self):
        if self.parent:
            # 检查层级深度
            current_parent = self.parent
            depth = 1
            while current_parent.parent:
                depth += 1
                current_parent = current_parent.parent
                
            if depth >= 7:
                raise ValidationError(_('分类层级不能超过7级'))
                
            if self.level <= self.parent.level:
                raise ValidationError(_('子类目的层级必须大于父类目的层级'))
        elif self.level != 1:
            raise ValidationError(_('没有父类目时，必须是一级分类'))

class SPU(models.Model):
    """SPU商品"""
    PRODUCT_TYPE_CHOICES = [
        ('math_design', '设计款'),
        ('ready_made', '现货款'),
        ('raw_material', '材料'),
        ('packing_material', '包材'),
    ]

    PRODUCTION_PROCESS_CHOICES = [
        ('metal', '金属类'),
        ('resin', '树脂类'),
        ('plush', '毛绒类'),
        ('plastic', '塑料类'),
    ]

    code = models.CharField(_('SPU编码'), max_length=50, unique=True)
    name = models.CharField(_('SPU名称'), max_length=100)
    product_type = models.CharField(_('产品类型'), max_length=20, choices=PRODUCT_TYPE_CHOICES)
    remark = models.TextField(_('备注'), blank=True, null=True)
    sales_channel = models.CharField(_('销售渠道'), max_length=20, blank=True, null=True)
    design_elements = models.CharField(
        _('设计元素'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('设计元素，如：蝴蝶')
    )
    production_process = models.CharField(
        _('生产工艺'),
        max_length=20,
        choices=PRODUCTION_PROCESS_CHOICES,
        blank=True,
        null=True,
        help_text=_('主要生产工艺')
    )
    brand = models.ForeignKey(
        Brand,
        verbose_name=_('品牌'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_('商品分类'),
        on_delete=models.PROTECT
    )
    poc = models.ForeignKey(
        User,
        verbose_name=_('产品专员'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('SPU')
        verbose_name_plural = _('SPU列表')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Product(models.Model):
    """SKU商品"""
    PLATING_PROCESS_CHOICES = (
        ('none', '无电镀'),
        ('18k_gold', '18K金'),
        ('18k_silver', '18K银'),
    )

    code = models.CharField(_('SKU编码'), max_length=50, unique=True)
    name = models.CharField(_('SKU名称'), max_length=100)
    spu = models.ForeignKey(
        SPU,
        verbose_name=_('所属SPU'),
        on_delete=models.CASCADE,
        related_name='products'
    )
    material = models.CharField(_('材质'), max_length=50)
    color = models.CharField(_('颜色'), max_length=50)
    plating_process = models.CharField(
        _('电镀工艺'),
        max_length=20,
        choices=PLATING_PROCESS_CHOICES,
        default='none'
    )
    surface_treatment = models.CharField(
        _('表面处理'),
        max_length=100,
        null=True,
        blank=True
    )
    weight = models.DecimalField(
        _('重量(g)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    length = models.IntegerField(_('长(mm)'), null=True, blank=True)
    width = models.IntegerField(_('宽(mm)'), null=True, blank=True)
    height = models.IntegerField(_('高(mm)'), null=True, blank=True)
    other_dimensions = models.CharField(
        _('其他尺寸'),
        max_length=25,
        null=True,
        blank=True
    )
    suppliers_list = models.TextField(_('供应商列表'), default='[]', blank=True)
    main_image = models.ImageField(
        _('主图'),
        upload_to=product_image_path,
        null=True,
        blank=True
    )
    images = models.JSONField(
        _('图片列表'),
        default=list,
        blank=True,
        help_text=_('存储多张图片的URL列表')
    )
    is_reviewed = models.BooleanField(_('是否已审核'), default=False)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('SKU')
        verbose_name_plural = _('SKU列表')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}" 