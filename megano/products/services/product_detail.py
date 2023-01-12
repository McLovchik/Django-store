from typing import Dict

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet
from django.http import HttpRequest
from dynamic_preferences.registries import global_preferences_registry

from ..models import Product


class CurrentProduct:
    def __init__(self, **kwargs) -> None:
        if 'slug' in kwargs:
            self.product = Product.objects.get(slug=kwargs['slug'])
        elif 'instance' in kwargs:
            self.product = kwargs['instance']
        else:
            raise ValueError

    @property
    def get_product(self) -> Product:
        return self.product

    @property
    def get_tags(self) -> QuerySet:
        tags = self.product.tags.all()
        return tags

    @property
    def get_reviews(self) -> QuerySet:
        reviews = self.product.product_comments.all()
        return reviews

    # @classmethod
    # def get_review_page(cls, queryset: QuerySet, page: int) -> Dict:
    #     """
    #     Method for getting reviews page to pass to javascript. Returns dict with queryset page reviews
    #     and data for pagination
    #     """
    #     reviews_count = queryset.count()
    #     reviews = queryset.values('author', 'user__avatar', 'content', 'added')
    #     OPTIONS = global_preferences_registry.manager().by_name()
    #     paginator = Paginator(reviews, per_page=OPTIONS['review_size_page'])
    #     page_obj = paginator.get_page(page)
    #     json_dict = {
    #         'comments': list(page_obj.object_list),
    #         'has_previous': None if page_obj.has_previous() is False
    #         else "previous",
    #         'previous_page_number': page_obj.number - 1,
    #         'num_pages': page_obj.paginator.num_pages,
    #         'number': page_obj.number,
    #         'has_next': None if page_obj.has_next() is False
    #         else "next",
    #         'next_page_number': page_obj.number + 1,
    #         'empty_pages': None if page_obj.paginator.num_pages < 2
    #         else "not_empty",
    #         'reviews_count': reviews_count,
    #         'media': settings.MEDIA_URL
    #     }
    #     return json_dict


# def context_pagination(request: HttpRequest, queryset: QuerySet, size_page: int = 3) -> Paginator:
#     """
#     Function for creating pagination
#     """
#     paginator = Paginator(queryset, size_page)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return page_obj
