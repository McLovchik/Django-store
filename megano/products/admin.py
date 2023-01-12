from django.contrib import admin
from .models import ProductCategory, Product, ProductImage, ProductComment
from django.utils.safestring import mark_safe
from .forms import ProductImageForm


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'icon')
    list_filter = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',), }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('main_image', 'id', 'name', 'category', 'limited', 'tags')
    list_display_links = ('main_image', 'name')
    list_filter = ('category', 'tags', 'limited')
    search_fields = ('name', 'category')
    prepopulated_fields = {'slug': ('name', 'code'), }


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    form = ProductImageForm
    fields = ['image', 'product']


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'content', 'added')
    list_filter = ('author_name', 'added')
    search_fields = ('author_name', 'added')
