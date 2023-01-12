from decimal import Decimal

from django.conf import settings
from products.models import Product
from ..utils import check_stock


class AnonymCart:
    """
    Класс корзины анонимного пользователя
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, update_quantity: bool = False):
        """Добавление товара в корзину или обновление его количества"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            delta = quantity - self.cart[product_id]['quantity']
            if check_stock(product, delta):
                self.cart[product_id]['quantity'] = quantity
                self.save()
                return True
            return False
        else:
            delta = quantity
            if check_stock(product, delta):
                self.cart[product_id]['quantity'] += quantity
                self.save()
                return True
            return False

    def save(self):
        """Отметка сессии как измененной"""
        self.session.modified = True

    def remove(self, product: Product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            product.quantity += self.cart[product_id]['quantity']
            product.save()
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Проходим по товарам корзины и получаем соответствующие объекты Product"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = float(item['price'])
            # item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """Получение количества товаров в корзине"""
        return len(self.cart.values())

    def total_sum(self):
        """Получение общей стоимости товаров в корзине"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """Очистка корзины"""
        del self.session[settings.CART_SESSION_ID]
        self.save()
