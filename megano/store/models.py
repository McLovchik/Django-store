from decimal import Decimal

from django.db import models
from users.models import User
from products.models import Product


class Order(models.Model):
    """
    Модель заказа
    """

    DELIVERY_CHOICES = [
        ('reg', 'Regular'),
        ('exp', 'Express')
    ]

    PAYMENT_CHOICES = [
        ('card', 'Bank Card'),
        ('cash', 'From random account'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='orders',
                                 verbose_name='customer')
    fullname = models.CharField(max_length=128, null=True, blank=True, verbose_name='fullname')

    phone = models.CharField(max_length=16, null=True, blank=True, verbose_name='phone number')

    email = models.EmailField(null=True, blank=True, verbose_name='email')

    delivery = models.CharField(max_length=3, choices=DELIVERY_CHOICES, default='reg', verbose_name='delivery')
    payment_method = models.CharField(max_length=4, choices=PAYMENT_CHOICES, default='card',
                                      verbose_name='payment method')

    city = models.CharField(max_length=32, null=True, blank=True, verbose_name='city')
    address = models.TextField(max_length=256, null=True, blank=True, verbose_name='address')

    in_order = models.BooleanField(default=False, verbose_name='in order')
    paid = models.BooleanField(default=False, verbose_name='order is payed')
    payment_error = models.CharField(max_length=50, null=True, blank=True, verbose_name='payment error')

    ordered = models.DateTimeField(null=True, blank=True, verbose_name='order placement date')
    braintree_id = models.CharField(max_length=150, blank=True, verbose_name='transaction id')  # убрать

    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='delivery cost')

    @property
    def total_sum(self) -> Decimal:
        """Метод получения общей стоимости товаров в заказе"""
        total = Decimal(0.00)
        for order_product in self.order_products.all():
            total += order_product.product.price * order_product.quantity
        return Decimal(total)

    @property
    def final_total_sum(self):
        return self.total_sum + self.delivery_cost

    def __str__(self):
        return f'{"Order"} №{self.id}'

    def name(self):
        return self.__str__()

    def __len__(self) -> int:
        """Метод получения количества товаров в заказе"""
        return len(self.order_products.all())

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'


class OrderProduct(models.Model):
    """
    Модель товара в заказе
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    quantity = models.IntegerField(null=True, default=1, verbose_name='quantity')

    def __str__(self):
        return f"{'OrderProduct'} №{self.id}"

    def name(self):
        return self.__str__()

    class Meta:
        verbose_name = 'order product'
        verbose_name_plural = 'order products'
