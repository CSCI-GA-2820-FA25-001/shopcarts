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

"""
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, ShopCarts, Items
from .factories import ShopCartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Items).delete()
        db.session.query(ShopCarts).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "ShopCarts Demo REST API Service")

    # Todo: Add your test cases here...
    ############################################################
    # Utility function to bulk create shopcarts
    ############################################################
    def _create_shopcarts(self, count: int = 1) -> list:
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopCartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shopcart",
            )
            new_shopcart = response.get_json()
            test_shopcart.shopcart_id = new_shopcart["shopcart_id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_shopcart_list(self):
        """It should Get a list of Shopcarts"""
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_create_shopcart(self):
        """It should Create a new shopcart"""
        test_shopcart = ShopCartFactory()
        logging.debug("Test shopcart: %s", test_shopcart.serialize())
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_id"], test_shopcart.customer_id)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_id"], test_shopcart.customer_id)

    def test_get_shopcart(self):
        """It should Get a single ShopCart"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.shopcart_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["shopcart_id"], test_shopcart.shopcart_id)

    def test_get_shopcart_not_found(self):
        """It should not Get a ShopCart thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_delete_shopcart(self):
        """It should Delete a shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.shopcart_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_shopcart.shopcart_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_shopcart(self):
        """It should Delete a shopcart even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_create_shopcart_item(self):
        """It should Create a new shopcart item"""
        test_shopcart = self._create_shopcarts(1)[0]
        shopcart_id = test_shopcart.shopcart_id

        # Create a test item using the factory
        test_item = ItemFactory()
        logging.debug("Test item: %s", test_item.serialize())

        response = self.client.post(
            f"{BASE_URL}/{shopcart_id}/items",
            json=test_item.serialize(),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_item = response.get_json()
        self.assertEqual(new_item["product_id"], test_item.product_id)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertAlmostEqual(
            float(new_item["price"]), float(test_item.price), places=2
        )
        self.assertEqual(new_item["shopcart_id"], shopcart_id)

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fetched_item = response.get_json()
        self.assertEqual(fetched_item["item_id"], new_item["item_id"])

    def test_list_shopcart_items(self):
        """It should list all items in a shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        shopcart_id = test_shopcart.shopcart_id

        created_items = []
        for _ in range(3):
            test_item = ItemFactory()
            response = self.client.post(
                f"{BASE_URL}/{shopcart_id}/items",
                json=test_item.serialize(),
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_items.append(response.get_json())

        response = self.client.get(f"{BASE_URL}/{shopcart_id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(created_items))
        created_ids = sorted(item["item_id"] for item in created_items)
        returned_ids = sorted(item["item_id"] for item in data)
        self.assertEqual(returned_ids, created_ids)
        created_lookup = {item["item_id"]: item for item in created_items}
        for item in data:
            self.assertEqual(item["shopcart_id"], shopcart_id)
            self.assertIn(item["item_id"], created_lookup)
            expected = created_lookup[item["item_id"]]
            self.assertEqual(item["product_id"], expected["product_id"])
            self.assertEqual(item["quantity"], expected["quantity"])
            self.assertAlmostEqual(
                float(item["price"]),
                float(expected["price"]),
                places=2,
            )

    def test_list_shopcart_items_empty(self):
        """It should return an empty list when a shopcart has no items"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.shopcart_id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data, [])

    def test_list_shopcart_items_not_found(self):
        """It should return 404 when listing items for a missing shopcart"""
        response = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shopcart_item(self):
        """It should read an item from a shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ItemFactory()
        create_resp = self.client.post(
            f"{BASE_URL}/{test_shopcart.shopcart_id}/items",
            json=test_item.serialize(),
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created_item = create_resp.get_json()

        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.shopcart_id}/items/{created_item['item_id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["item_id"], created_item["item_id"])
        self.assertEqual(data["shopcart_id"], test_shopcart.shopcart_id)
        self.assertEqual(data["product_id"], created_item["product_id"])
        self.assertEqual(data["quantity"], created_item["quantity"])
        self.assertAlmostEqual(
            float(data["price"]), float(created_item["price"]), places=2
        )

    def test_get_shopcart_item_not_found(self):
        """It should return 404 when the item is missing from the shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.shopcart_id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_delete_shopcart_item(self):
        """It should Delete a Shopcart Item"""
        # create a shopcart and add an item
        test_shopcart = self._create_shopcarts(1)[0]
        shopcart_id = test_shopcart.shopcart_id
        test_item = ItemFactory()
        create_resp = self.client.post(
            f"{BASE_URL}/{shopcart_id}/items",
            json=test_item.serialize(),
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created_item = create_resp.get_json()

        # delete the item
        response = self.client.delete(
            f"{BASE_URL}/{shopcart_id}/items/{created_item['item_id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # make sure it was deleted
        response = self.client.get(
            f"{BASE_URL}/{shopcart_id}/items/{created_item['item_id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_shopcart_item(self):
        """It should Delete a Shopcart Item even if it doesn't exist"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.shopcart_id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
    def test_update_shopcart_item(self):
        """It should Update an existing ShopCart Item"""
        # create a shopcart to hold the item
        test_shopcart = self._create_shopcarts(1)[0]

        # create an item to update (via factory, like the Pet template)
        test_item = ItemFactory(quantity=2, price=10.00)  # unit price = 5.00
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.shopcart_id}/items",
            json=test_item.serialize(),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the item
        new_item = response.get_json()
        logging.debug(new_item)

        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.shopcart_id}/items/{new_item['item_id']}",
            json={
                "quantity": new_item["quantity"],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = response.get_json()
        self.assertEqual(updated_item["item_id"], new_item["item_id"])
        self.assertEqual(updated_item["shopcart_id"], test_shopcart.shopcart_id)


class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a shopcart id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_shopcart_no_data(self):
        """It should not Create a ShopCart with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_shopcart_no_content_type(self):
        """It should not Create a ShopCart with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_wrong_content_type(self):
        """It should not Create a ShopCart with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
