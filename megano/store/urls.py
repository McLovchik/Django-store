from django.urls import path
from .views import CartView, CartAdd, CartRemove, OrderingStepOne, OrderingStepOneAnonym, OrderingStepTwo, \
    OrderingStepThree, OrderingStepFour, PaymentView, PaymentWithCardView, PaymentWithAccountView, \
    payment_done, payment_canceled, HistoryOrdersView, HistoryOrderDetailView


urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('add_product_in_cart/<int:product_id>/', CartAdd.as_view(), name='add-product-in-cart'),
    path('delete_product_from_cart/<int:product_id>/', CartRemove.as_view(), name='delete-product-from-cart'),

    path('ordering/step_one/', OrderingStepOne.as_view(), name='ordering-step-one'),
    path('ordering/step_one_anonym/', OrderingStepOneAnonym.as_view(), name='ordering-step-one-anonym'),
    path('ordering/step_two/', OrderingStepTwo.as_view(), name='ordering-step-two'),
    path('ordering/step_three/', OrderingStepThree.as_view(), name='ordering-step-three'),
    path('ordering/step_four/', OrderingStepFour.as_view(), name='ordering-step-four'),

    path('payment/<int:order_id>/', PaymentView.as_view(), name='payment'),
    path('payment/card/<int:order_id>/', PaymentWithCardView.as_view(), name='payment-card'),
    path('payment/account/<int:order_id>/', PaymentWithAccountView.as_view(), name='payment-account'),
    path('payment_done/', payment_done, name='payment-done'),
    path('payment_canceled/', payment_canceled, name='payment-canceled'),

    path('history_orders/', HistoryOrdersView.as_view(), name='history-orders'),
    path('history_order/<int:order_id>/', HistoryOrderDetailView.as_view(), name='history-order-detail'),
]
