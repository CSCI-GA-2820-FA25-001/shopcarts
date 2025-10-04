######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""Test cases for ShopCart and Item models."""

# pylint: disable=duplicate-code
import os
import logging
from decimal import Decimal
from unittest import TestCase
from wsgi import app
from service.models import ShopCarts, Items, DataValidationError, db
from .factories import ShopCartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopCartModel(TestCase):
    """Test Cases for ShopCart and Item models"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Items).delete()
        db.session.query(ShopCarts).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ##################################################################
    #  T E S T   C A S E S
    ##################################################################

    def test_create_shopcart(self):
        """It should create a shopcart with a unique identifier"""
        shopcart = ShopCartFactory()
        shopcart.create()

        self.assertIsNotNone(shopcart.shopcart_id)
        self.assertGreater(shopcart.shopcart_id, 0)
        stored = ShopCarts.find(shopcart.shopcart_id)
        self.assertEqual(stored.customer_id, shopcart.customer_id)

    def test_prevent_duplicate_customer_shopcart(self):
        """It should prevent multiple active shopcarts per customer"""
        first = ShopCarts(customer_id=888)
        first.create()

        duplicate = ShopCarts(customer_id=888)
        with self.assertRaises(DataValidationError):
            duplicate.create()

    def test_read_existing_shopcart(self):
        """It should read an existing shopcart with its items"""
        shopcart = ShopCartFactory()
        item = ItemFactory(product_id=321, quantity=2, price=Decimal("9.99"))
        shopcart.items.append(item)
        shopcart.create()

        found = ShopCarts.find(shopcart.shopcart_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.shopcart_id, shopcart.shopcart_id)
        self.assertEqual(len(found.items), 1)
        self.assertEqual(found.items[0].product_id, 321)
        self.assertEqual(found.items[0].quantity, 2)

    def test_read_nonexistent_shopcart(self):
        """It should return None when the shopcart does not exist"""
        self.assertIsNone(ShopCarts.find(0))

    def test_update_shopcart_items(self):
        """It should update item quantities and refresh timestamps"""
        shopcart = ShopCartFactory()
        shopcart.items.append(ItemFactory(quantity=1))
        shopcart.create()

        previous_updated = shopcart.updated_at
        shopcart.items[0].quantity = 3
        shopcart.update()

        refreshed = ShopCarts.find(shopcart.shopcart_id)
        self.assertEqual(refreshed.items[0].quantity, 3)
        self.assertNotEqual(refreshed.updated_at, previous_updated)
        self.assertGreaterEqual(refreshed.updated_at, previous_updated)

    def test_delete_shopcart_cascades_items(self):
        """It should delete a shopcart and cascade delete its items"""
        shopcart = ShopCartFactory()
        shopcart.items.extend([ItemFactory(), ItemFactory()])
        shopcart.create()

        cart_id = shopcart.shopcart_id
        shopcart.delete()

        self.assertIsNone(ShopCarts.find(cart_id))
        remaining = Items.query.filter_by(shopcart_id=cart_id).count()
        self.assertEqual(remaining, 0)

    def test_list_all_shopcarts(self):
        """It should list all shopcarts with their items"""
        customer_ids = [101, 102, 103]
        for customer_id in customer_ids:
            cart = ShopCarts(customer_id=customer_id)
            cart.items.append(ItemFactory())
            cart.create()

        found = ShopCarts.all()
        self.assertEqual(len(found), len(customer_ids))
        self.assertTrue(all(cart.items for cart in found))

    def test_item_quantity_geq_one(self):
        """It should enforce quantity validations"""
        with self.assertRaises(DataValidationError):
            Items(product_id=1, quantity=0)

        with self.assertRaises(DataValidationError):
            Items(product_id=1, quantity=-1)
