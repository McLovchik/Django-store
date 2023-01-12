from decimal import Decimal

from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import IntegerPreference, DecimalPreference
from dynamic_preferences.preferences import Section
from django.core.exceptions import ValidationError


general = Section('general')


@global_preferences_registry.register
class MaxFileSize(IntegerPreference):
    section = general
    name = 'max_size_file'
    help_text = 'Set the max image file sizes in MB'
    default = 2
    required = True
    verbose_name = 'Max image files size'


@global_preferences_registry.register
class ReviewsSizePage(IntegerPreference):
    section = general
    name = 'review_size_page'
    help_text = 'Set the count reviews, showing on product detail page'
    default = 3
    required = True
    verbose_name = 'Reviews size page'

    def validate(self, value):
        if value < 1:
            raise ValidationError('Wrong size value! Must be more than 0')


@global_preferences_registry.register
class ShippingRegularPrice(DecimalPreference):
    section = general
    name = 'regular_shipping'
    help_text = 'Set the regular shipping amount'
    default = Decimal('200.00')
    required = True
    verbose_name = 'Regular shipping price'

    def validate(self, value):
        if value < 0:
            raise ValidationError('Wrong price value! Must be positive')


@global_preferences_registry.register
class ShippingExpressPrice(DecimalPreference):
    section = general
    name = 'express_shipping'
    help_text = 'Set the express shipping amount'
    default = Decimal('500.00')
    required = True
    verbose_name = 'Express shipping price'

    def validate(self, value):
        if value < 0:
            raise ValidationError('Wrong price value! Must be positive')


@global_preferences_registry.register
class CountPopularProducts(IntegerPreference):
    section = general
    name = 'count_popular_products'
    help_text = 'Set the count popular products, showing on main page'
    default = 8
    required = True
    verbose_name = 'Count popular products'

    def validate(self, value):
        if value < 1:
            raise ValidationError('Wrong count value! Must be more than 1')


@global_preferences_registry.register
class CountLimitedProducts(IntegerPreference):
    section = general
    name = 'count_limited_products'
    help_text = 'Set the count limited products, showing on main page'
    default = 16
    required = True
    verbose_name = 'Count limited products'

    def validate(self, value):
        if value < 1:
            raise ValidationError('Wrong count value! Must be more than 0')

