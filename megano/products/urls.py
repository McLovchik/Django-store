from django.urls import path
from .views import ProductDetailView, IndexView, FullCatalogView, AllCardForAjax


urlpatterns = [
    path('product-detail/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('', IndexView.as_view(), name='index-url'),
    path('catalog/', FullCatalogView.as_view(), name='catalog-url'),
    path('async_catalog/', AllCardForAjax.as_view(), name='ajax-full'),
]
