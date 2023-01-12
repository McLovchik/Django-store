
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from ..models import Order


User = get_user_model()


class StoreServiceMixin:

    @classmethod
    def get_all_orders(cls, user: User) -> QuerySet:
        """
        Get all user Orders
        """
        orders = Order.objects.filter(customer=user, in_order=True)
        return orders

    @classmethod
    def get_last_order(cls, user: User) -> QuerySet:
        """
        Get last user Order
        """
        order = cls.get_all_orders(user=user).last()
        return order

