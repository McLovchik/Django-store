from typing import Callable

from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from django.urls import reverse
from taggit.managers import TaggableManager


User = get_user_model()


class ProductCategory(MPTTModel):
    """
    Модель категории товаров
    """
    name = models.CharField(max_length=24, null=True, verbose_name='название категории товара')
    slug = models.SlugField(verbose_name='slug', unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    icon = models.ImageField(upload_to='icons_for_categories/', verbose_name='icon')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'product categories'
        verbose_name = 'product category'

    class MPTTMeta:
        order_insertion_by = ['name']

    @property
    def icon_url(self):
        if self.icon and hasattr(self.icon, 'url'):
            return self.icon.url

    # def save(self, *args, **kwargs) -> Callable:
    #     """
    #     Method overridden to remove old files and add permissions
    #     """
    #     if self.pk is not None:
    #         old_self = ProductCategory.objects.get(pk=self.pk)
    #         if old_self.image and self.image != old_self.image:
    #             old_self.image.delete(False)
    #         if old_self.icon and self.icon != old_self.icon:
    #             old_self.icon.delete(False)
    #     return super(ProductCategory, self).save(*args, **kwargs)


class Product(models.Model):
    """
    Модель товара
    """
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products',
                                 verbose_name='product category',)
    name = models.CharField(max_length=128, verbose_name='product name')
    main_image = models.ImageField(upload_to='products_images/', blank=True, null=True)
    code = models.CharField(max_length=10, null=True, blank=True, verbose_name='product code')
    slug = models.SlugField(db_index=True, verbose_name='product slug', unique=True)
    description = models.TextField(max_length=1024, null=True, verbose_name='product description')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='price')
    quantity = models.IntegerField(verbose_name='quantity')
    date_added = models.DateTimeField(verbose_name='date added', auto_now_add=True)
    limited = models.BooleanField(default=False, verbose_name='limited edition')
    tags = TaggableManager()

    def __str__(self):
        return self.name

    # def get_absolute_url(self) -> Callable:
    #     return reverse('product-detail', kwargs={'slug': self.slug})

    @property
    def image_url(self):
        if self.main_image and hasattr(self.main_image, 'url'):
            return self.main_image.url

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        db_table = 'products'


class ProductImage(models.Model):
    image = models.ImageField(upload_to='products_images/', blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='Товар')


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    author_name = models.CharField(verbose_name='author name', max_length=32, null=True, blank=True)
    content = models.TextField(verbose_name='content', max_length=1024, null=True)
    added = models.DateTimeField(verbose_name='added', auto_now_add=True, null=True)

    def __str__(self) -> str:
        return f'Comments for {str(self.product)}'

    class Meta:
        verbose_name = 'product comment'
        verbose_name_plural = 'product comments'
        db_table = 'comments'
