from django import template
from products.models import ProductCategory


register = template.Library()


@register.inclusion_tag('elements/categories.html')
def show_categories():
    categories = ProductCategory.objects.all()
    return {'categories': categories}
