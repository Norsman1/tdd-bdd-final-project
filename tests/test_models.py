# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)
    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_no_update_product_with_id_zero(self):
        """It should not Update a Product with id zero"""
        product = ProductFactory()
        product.id = None
        product.create()
        product.id = 0
        self.assertRaises(Exception, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        # Assert if the products list is empty, indicating that there are no products
        # in the database at the beginning of the test case.
        # Use for loop to create five Product objects using a ProductFactory()
        # and call the create() method on each product to save them to the database.
        # Fetch all products from the database again using product.all()
        # Assert if the length of the products list is equal to 5, to verify that the five
        # products created in the previous step have been successfully added to the database.

        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_deserialization_nodata_error(self):
        """It should Generate an Exception if Bad or No Data is Passed to Deserialization"""
        # buid dictionary of values to test serialization
        test_product = None
        product = ProductFactory()
        product.create()
        self.assertRaises(Exception, product.deserialize, test_product)

    def test_no_data_exception_error(self):
        """It should Generate a No Data Attribute Error in Deserialization"""
        # buid dictionary of values to test serialization
        test_product = {}
        product = ProductFactory()
        product.create()
        self.assertRaises(Exception, product.deserialize, test_product)

    def test_invalid_attribute_error(self):
        """It should Generate an Invalid Category Error in Deserialization"""
        # buid dictionary of values to test serialization
        test_product = {
            "id": 1,
            "name": "Nike Sneakers",
            "description": "Kids Shoes",
            "category": "Mexican",
            "price": 250,
            "available": True}
        product = ProductFactory()
        product.create()
        self.assertRaises(Exception, product.deserialize, test_product)

    def test_bad_data_error(self):
        """It should Generate a Bad or No Data Error in Deserialization"""
        # buid dictionary of values to test serialization
        test_product = {
                "id": True,
                "name": "Nike Sneakers",
                "description": "Kids Shoes",
                "category": "CLOTHS",
                "price": "Fifty Cents",
                "available": 47}
        product = ProductFactory()
        product.create()
        self.assertRaises(Exception, product.deserialize, test_product)

    def test_invalid_boolean_attribute_error(self):
        """It should Generate an Invalid Boolean Error in Deserialization"""
        # buid dictionary of values to test serialization
        test_product = {
                "id": 1,
                "name": "Nike Sneakers",
                "description": "Kids Shoes",
                "category": "Mexican",
                "price": 250,
                "available": 23}
        product = ProductFactory()
        product.create()
        self.assertRaises(Exception, product.deserialize, test_product)

    def test_find_by_price(self):
        """It should Find a Product based upon its Price"""
        product = Product.all()
        product = ProductFactory()
        product.id = None
        product.create()
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        price = "12.50"
        product = product.find_by_price(price)
        print("product is %s", product)
