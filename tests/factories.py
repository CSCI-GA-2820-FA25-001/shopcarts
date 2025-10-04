"""Factories to create model instances for testing."""

from decimal import Decimal

import factory

from service.models import ShopCarts, Items


class ShopCartFactory(factory.Factory):
    """Create shopcarts for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        model = ShopCarts

    shopcart_id = None
    customer_id = factory.Sequence(lambda n: n + 1000)


class ItemFactory(factory.Factory):
    """Create items for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        model = Items

    item_id = None
    product_id = factory.Sequence(lambda n: n + 2000)
    quantity = factory.Iterator([1, 2, 3])
    price = factory.LazyFunction(lambda: Decimal("9.99"))
