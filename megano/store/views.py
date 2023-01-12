import random
from typing import Callable
import datetime

from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import View
from .services.cart import CartService
from .models import OrderProduct, Order
from products.models import Product
from .forms import OrderingStepOneForm, OrderingStepTwoForm, OrderingStepThreeForm
from users.forms import RegisterForm
from users.services import reset_phone_format, get_auth_user
from django.contrib.auth import get_user_model, login
from application_settings.dynamic_preferences_registry import global_preferences_registry
from django.http.response import Http404
from .services.payment_errors import PAYMENT_ERRORS
from .services.store_service import StoreServiceMixin
from django.views.generic import ListView, DetailView


def about_view(request):
    return render(request, 'store/about.html')


class CartView(View):
    """
    Представление корзины
    ::Страница: Корзина
    """

    @classmethod
    def get(cls, request: HttpRequest):
        cart = CartService(request)

        # discounted_prices = []
        quantities = []

        items = cart.get_goods()
        for item in items:
            # discounted_price = discount_service.get_discounted_price(item)

            if isinstance(item, OrderProduct):  # ??
                # item.final_price = discounted_price
                # item.save()
                quantities.append(item.quantity)
            else:
                # item['final_price'] = discounted_price
                quantities.append(item['quantity'])

            # discounted_prices.append(discounted_price)

        products = items
        total = cart.get_quantity
        total_price = cart.get_total_sum

        context = {
            'items': products,
            'total': total,
            'total_price': total_price
        }

        return render(request, 'store/cart/cart.html', context=context)

    @classmethod
    def post(cls, request: HttpRequest, product_id):
        cart = CartService(request)

        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('amount'))

        if quantity < 1:
            quantity = 1
        if int(product_id) == product.id:
            cart.add_to_cart(product, quantity, update_quantity=True)
        else:
            cart.update_product(product, quantity, product_id)

        return redirect('')  # orders:cart_detail


class CartAdd(View):
    """
    Добавление позиций в корзине
    ::Страница: Корзина
    """
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        product = get_object_or_404(Product, id=product_id)
        cart.add_to_cart(product, quantity=1, update_quantity=False)
        return redirect(request.META.get('HTTP_REFERER'))

    def post(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('amount'))
        cart.add_to_cart(product, quantity=quantity, update_quantity=False)
        # added = cart.add_to_cart(product, quantity=quantity, update_quantity=False)
        # if added:
        #     messages.add_message(request, settings.SUCCESS_ADD_TO_CART,
        #                          f'{product.name} was added to cart succesfully.')
        # else:
        #     messages.add_message(request, settings.ERROR_ADD_TO_CART,
        #                          f'The quantity in stock for {product.name} is not enough.')
        return redirect(request.META.get('HTTP_REFERER'))


class CartRemove(View):
    """
    Удаление позиции из корзины
    ::Страница: Корзина
    """
    def get(self, request: HttpRequest, product_id: int):
        cart = CartService(request)
        cart.remove_from_cart(product_id)
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class OrderingStepOne(View):
    """
    Представление первого шага оформления заказа
    ::Страница: Оформление заказа
    """
    form_class = OrderingStepOneForm
    template_name = 'store/ordering/step_one.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            initial = {
                'fullname': user.fullname,
                'email': user.email,
                'phone': user.phone,
                'delivery': 'exp',
                'payment': 'cash'
            }
        else:
            initial = {
                'delivery': 'exp',
                'payment': 'cash'
            }

        form = self.form_class(initial=initial)

        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:
                order = Order.objects.get(customer=request.user, in_order=False)
                fullname = form.cleaned_data['fullname']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']

                order.fullname = fullname
                order.email = email
                order.phone = phone
                order.save()

                return redirect('ordering-step-two')  #
            else:
                return redirect('login')

        return render(request, self.template_name, {'form': form})


class OrderingStepOneAnonym(View):
    """
    Представление первого шага оформления заказа для анонимного пользователя
    ::Страница: Оформление заказа
    """
    template_name = 'store/ordering/step_one_anonym.html'

    def get(self, request: HttpRequest) -> Callable:
        if request.user.is_authenticated:
            return redirect('ordering-step-one')
        form = RegisterForm()
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest) -> Callable:
        """
        Метод переопределен для слияние анонимной корзины
        с корзиной аутентифицированного пользователя
        """
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            old_cart = CartService(self.request)
            user = form.save()
            reset_phone_format(instance=user)
            login(request, get_auth_user(data=form.cleaned_data))
            new_cart = CartService(self.request)
            new_cart.merge_carts(old_cart)

            # discount_service = DiscountsService(new_cart)
            # items = new_cart.get_goods()
            # for item in items:
            #     discounted_price = discount_service.get_discounted_price(item)
            #     item.final_price = discounted_price
            #     item.save()

            order = Order.objects.get(customer=request.user, in_order=False)
            fullname = request.POST.get('fullname')
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            order.fullname = fullname
            order.email = email
            order.phone = phone
            order.save()
            return redirect('ordering-step-two')

        return render(request, self.template_name, {'form': form})


class OrderingStepTwo(View):
    """
    Представление второго шага оформления заказа
    ::Страница: Оформление заказа
    """
    form_class = OrderingStepTwoForm
    template_name = 'store/ordering/step_two.html'

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            initial = {
                'city': user.city,
                'address': user.address,
                'delivery': 'reg',
                'payment': 'cash'
            }
            form = self.form_class(initial=initial)
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('login')

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            delivery = form.cleaned_data['delivery']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']

            order.delivery = delivery
            order.city = city
            order.address = address

            if order.order_products.first():
                global_preferences = global_preferences_registry.manager()

                if order.delivery == 'reg':
                    if order.total_sum < 2000:
                        order.delivery_cost = global_preferences['general__regular_shipping']
                else:
                    order.delivery_cost = global_preferences['general__express_shipping']

            order.save()

            return redirect('ordering-step-three')
        return render(request, self.template_name, {'form': form})


class OrderingStepThree(View):
    """
    Представление третьего шага оформления заказа
    ::Страница: Оформление заказа
    """
    form_class = OrderingStepThreeForm
    template_name = 'store/ordering/step_three.html'

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            form = OrderingStepThreeForm
            return render(request, self.template_name, {'form': form})
        else:
            return redirect('login')

    def post(self, request: HttpRequest):
        form = self.form_class(request.POST)
        order = Order.objects.get(customer=request.user, in_order=False)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            order.payment_method = payment_method
            order.in_order = True
            order.ordered = datetime.datetime.today()
            order.save()
            return redirect('ordering-step-four')

        return render(request, self.template_name, {'form': form})


class OrderingStepFour(View):
    """
    Представление четвертого шага оформления заказа
    ::Страница: Оформление заказа
    """
    template_name = 'store/ordering/step_four.html'

    def get(self, request: HttpRequest):
        user = request.user
        if user.is_authenticated:
            order = Order.objects.filter(customer=user, in_order=True).last()
            return render(request, self.template_name, {'order': order})

        else:
            return redirect('login')


class PaymentView(View):
    """
    Оплата заказа. Логика направляется в зависимости от способа оплаты.
    ::Страница: Оплата заказа
    """
    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.payment_method == 'card':
            return redirect('payment-card', order_id)
        else:
            return redirect('payment-account', order_id)


class PaymentWithCardView(View):
    """
    Представление оплаты банковской картой
    ::Страница: Оплата заказа
    """
    template_name = 'store/payment/payment_card.html'

    def get(self, request: HttpRequest, order_id: int):
        try:
            order = get_object_or_404(Order, id=order_id)
        except Http404:
            order = None
        # client_token = braintree.ClientToken.generate()
        context = {'order': order}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, order_id: int):
        order = get_object_or_404(Order, id=order_id)
        nonce = request.POST.get('payment_card_nonce', None)
        if nonce:
            nonce = "".join(nonce.split())
            if nonce.endswith('0'):
                order.payment_error = random.choice(PAYMENT_ERRORS)
                order.save()
                return render(request, 'store/payment/payment_process.html', {'result': False})
            else:
                order.paid = True
                order.save()
                return render(request, 'store/payment/payment_process.html', {'result': True})


class PaymentWithAccountView(View):
    """
    Представление оплаты рандомным счетом
    ::Страница: Оплата заказа
    """
    template_name = 'store/payment/payment_account.html'

    def get(self, request: HttpRequest, order_id: int):
        order = get_object_or_404(Order, id=order_id)
        context = {'order': order}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, order_id: int):
        order = get_object_or_404(Order, id=order_id)
        nonce = request.POST.get('payment_account_nonce', None)
        if nonce:
            print(f'nonce-{nonce}, order_id-{order_id}')
            nonce = "".join(nonce.split())
            if nonce.endswith('0'):
                order.payment_error = random.choice(PAYMENT_ERRORS)
                order.save()
                return render(request, 'store/payment/payment_process.html', {'result': False})
            else:
                order.paid = True
                order.save()
                return render(request, 'store/payment/payment_process.html', {'result': True})


def payment_done(request):
    """
    Представление удачной оплаты
    ::Страница: Оплата заказа
    """
    return render(request, 'store/payment/payment_successful.html')


def payment_canceled(request):
    """
    Представление неудачной оплаты
    ::Страница: Оплата заказа
    """
    return render(request, 'store/payment/payment_unsuccessful.html')


class HistoryOrdersView(StoreServiceMixin, ListView):
    """
    Представление истории заказов
    ::Страница: История заказов
    """
    model = Order
    context_object_name = 'orders'
    template_name = 'store/history_orders.html'

    def get_queryset(self):
        queryset = self.get_all_orders(user=self.request.user).order_by('-ordered')
        return queryset


class HistoryOrderDetailView(DetailView):
    """
    Детальное представление заказа
    ::Страница: Детальная страница заказа
    """

    model = Order

    def get(self, request, *args, **kwargs):
        pk = kwargs['order_id']
        order = self.model.objects.prefetch_related('order_products').get(id=pk)
        return render(request, 'store/history_order_detail.html', context={'order': order})
