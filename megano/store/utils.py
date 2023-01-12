from products.models import Product


def check_stock(product: Product, delta: int) -> bool:
    """ Проверка наличия на складе """
    if product.quantity >= delta:
        product.quantity -= delta
        product.save()
        return True
    return False
