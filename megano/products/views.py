from typing import Dict, Callable, Union, Iterable

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin
from .models import Product, ProductImage
from application_settings.dynamic_preferences_registry import global_preferences_registry
from .services.product_detail import CurrentProduct
from .forms import ReviewForm
from django.forms import HiddenInput
from .services.products import get_popular_products, get_limited_products, get_random_categories
from django.views import View
from .services.catalog import CatalogByCategoriesMixin


class ProductDetailView(FormMixin, DetailView):
    """
    Детальная страница продукта
    ::Страница: Детальная страница продукта
    """
    model = Product
    context_object_name = 'product'
    template_name = 'products/product_detail.html'
    slug_url_kwarg = 'slug'
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('product-detail', kwargs={'slug': self.get_object().slug})

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        product = CurrentProduct(instance=context['product'])
        reviews = product.get_reviews

        context = {
            'reviews_count': reviews.count(),
            'tags': product.get_tags,
            'comments': reviews,
            **context
        }

        if self.request.user.is_authenticated:
            context['form'] = ReviewForm(initial={'product': self.object, 'user': self.request.user})
            context['form'].fields['author_name'].required = False
            context['form'].fields['author_name'].widget = HiddenInput()
            context['form'].fields['author_name'].widget.attrs['required'] = False
            context['form'].fields['user'].widget = HiddenInput()
        else:
            context['form'] = ReviewForm(initial={'product': self.object})
            context['form'].fields['user'].required = False
            context['form'].fields['user'].widget = HiddenInput()
            context['form'].fields['user'].widget.attrs['required'] = False

        context['images'] = ProductImage.objects.all().filter(product_id=product.product.id)

        return context

    def get_form(self, form_class=form_class):
        form = super(ProductDetailView, self).get_form(form_class)
        return form

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super(ProductDetailView, self).form_valid(form)


class IndexView(ListView):
    """
    Главная страница
    ::Страница: Главная
    """
    model = Product
    template_name = 'products/index.html'
    context_object_name = 'popular_products'

    def get_queryset(self) -> Iterable:
        OPTIONS = global_preferences_registry.manager().by_name()
        products = get_popular_products(count=OPTIONS['count_popular_products'])
        return products

    def get_context_data(self, **kwargs) -> Dict:
        context = super(IndexView, self).get_context_data(**kwargs)
        OPTIONS = global_preferences_registry.manager().by_name()
        limited_products = get_limited_products(count=OPTIONS['count_limited_products'])
        random_categories = get_random_categories()

        context['limited_products'] = limited_products
        context['random_categories'] = get_random_categories()
        return context


class FullCatalogView(CatalogByCategoriesMixin, View):
    """
    Класс-контроллер для отображения каталога-списка всех товаров
    ::Страница: Каталог
    """

    def get(self, request):
        """
        метод для гет-запроса контроллера для отображения каталога всех товаров с учётом параметров гет-запроса
        возможные параметры
            search - запрос пользователя из поисковой строки
            tag - выбранный тэг
            sort_type - тип сортировки
            page - страница пагинации
            slug - слаг категории товаров
        :return: рендер страницы каталога товаров определенной категории
        """
        # получаем параметры гет-запроса
        search, tag, sort_type, page, slug = self.get_request_params_for_full_catalog(request)

        # получаем товары в соответсвии с параметрами гет-запроса
        row_items_for_catalog, tags = self.get_full_data(tag, search, slug)

        # сортируем товары
        items_for_catalog, *_ = self.simple_sort(row_items_for_catalog, sort_type)

        # пагинатор
        paginator = Paginator(items_for_catalog, 8)
        page_obj = paginator.get_page(page)

        # кастомные параметры для рэнж-инпута в фильтре каталога
        maxi = self.get_max_price(items_for_catalog)
        mini = self.get_min_price(items_for_catalog)
        midi = round((maxi + mini) / 2, 2)

        # настройка кнопок пагинации
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)
        pages_list = self.custom_pagination_list(paginator, page)

        return render(
            request,
            'products/catalog.html',
            context={
                'page_obj': page_obj,
                'sort_type': sort_type,
                'mini': mini,
                'maxi': maxi,
                'midi': midi,
                'next_page': next_page,
                'prev_page': prev_page,
                'pages_list': pages_list,
                'tags': tags,
                'search': search,
                'tag': tag,
            })


class AllCardForAjax(CatalogByCategoriesMixin, View):
    """
    Класс-контроллер для отображения набора товаров в каталоге с учетом необходимых фильтров, сортировки и пагинации
    ::Страница: Каталог
    """

    def get(self, request):
        """
        метод для гет-запроса контроллера для отображения  набора товаров в каталоге
        с учетом необходимых фильтров, сортировки и пагинации без обновления изначальной страницы каталога
        get параметры :
            search - запрос пользователя из поисковой строки
            tag - выбранный тэг
            sort_type - тип сортировки
            page - страница пагинации
            slug - слаг категории товаров
        :param request: искомый запрос клиента
        :return: json с ключами:
                html - текст разметки необходимых карточек товаров с учетов входных условий
                current_state - вид и направление текущей использованной сортировки
                next_state - тип и направление сортировки для повторного запроса
                next_page - значение следующей доступной страницы пагинации
                prev_page - значение предыдущей доступной страницы пагинации
                pages_list - список доступных номеров страниц пагинации при данных входных условиях
        """

        search, tag, sort_type, page, slug = self.get_request_params_for_full_catalog(request)

        if not self.check_if_filter_params(request):
            # получаем товары без фильтра и актуальные стоимости
            row_items_for_catalog, tags = self.get_full_data(tag, search, slug)
        else:
            # получаем товары с фильтром и актуальные стоимости
            filter_data = self.get_data_from_form(request)
            row_items_for_catalog, sellers, tags = self.get_full_data_with_filters(
                search_query=search,
                search_tag=tag,
                slug=slug,
                filter_data=filter_data
            )

        items_for_catalog, next_state = self.simple_sort(row_items_for_catalog, sort_type)

        # пагинатор
        paginator = Paginator(items_for_catalog, 8)

        pages_list = self.custom_pagination_list(paginator, page)
        page_obj = paginator.get_page(page)

        # кнопки пагинации
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)

        context = {
            'pages_list': pages_list,
            'page_obj': page_obj,
            'sort_type': sort_type,
            'next_page': next_page,
            'prev_page': prev_page,
        }

        return JsonResponse({
            'html': render_to_string('products/elements/catalog_products.html', context=context),
            'current_state': sort_type,
            'next_state': next_state,
            'next_page': next_page,
            'prev_page': prev_page,
            'pages_list': pages_list,
            'sort_type': sort_type,
        })
