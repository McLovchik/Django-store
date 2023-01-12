import random
from typing import Union, List

from django.db.models import QuerySet, Count, Q, Min
from ..models import Product, ProductCategory


def get_popular_products(count: int) -> QuerySet:
    queryset = Product.objects.annotate(
        buying=Count('order_products__quantity', filter=Q(order_products__order__paid=True))
    ).order_by('-buying')[:count]
    return queryset


def get_limited_products(count: int) -> Union[QuerySet, bool]:
    queryset = Product.objects.filter(limited=True)[:count]
    if not list(queryset):
        return False
    return queryset


def get_categories() -> QuerySet:
    """
    Get all categories
    """
    categories = ProductCategory.objects.select_related('parent').all()
    return categories


def get_random_categories() -> Union[List, None]:
    """
    Function to get 3 random categories, if it has at least 1 product. And the annotate for each category with
    minimal price from this category products. Returns QuerySet with 3 random elements or False if Queryset is empty
    """
    categories = get_categories()
    queryset = categories.annotate(count=Count('products'), from_price=Min('products__price')).exclude(count=0)
    try:
        random_categories = random.choices(population=list(queryset), k=3)
    except IndexError:
        return None
    return random_categories
