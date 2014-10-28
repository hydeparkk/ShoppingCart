__author__ = 'hydeparkk'

import json
import unittest

from pymongo import MongoClient
from webtest import TestApp

from populate_db import populate_db
import app


TEST_DB = 'shopping-cart-test'


class SlugifyTests(unittest.TestCase):
    def test_return_lowercase_text(self):
        self.assertEqual(app.slugify('HYDECODE'), 'hydecode')

    def test_replace_space_with_dash(self):
        self.assertEqual(app.slugify('Hyde Code'), 'hyde-code')

    def test_remove_unnecessary_spaces(self):
        self.assertEqual(app.slugify('    Hyde    Code    '), 'hyde-code')

    def test_return_only_ascii_letters_and_numbers(self):
        self.assertEqual(app.slugify('qwerty12345!@#$%^&*()"><?:}{|-'),
                         'qwerty12345-')


class AppTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.client = MongoClient()
        self.db = self.client[TEST_DB]
        self.app = TestApp(app.shopping_cart_app)
        app.db = self.db
        # Populate database with random data
        populate_db(TEST_DB)

    def tearDown(self):
        self.client.drop_database('shopping-cart-test')

    def test_get_categories_request(self):
        req = self.app.get('/api/category')
        self.assertEqual(req.status, '200 OK')
        self.assertEqual(req.content_type, 'application/json')

    def test_get_categories(self):
        categories = json.loads(app.get_categories())
        self.assertEqual(len(categories), self.db.categories.count())
        self.assertEqual(sum([item['prod_amount'] for item in categories]),
                         self.db.products.count())

    def test_get_category_products_request(self):
        req = self.app.get('/api/category/cat-0')
        self.assertEqual(req.status, '200 OK')
        self.assertEqual(req.content_type, 'application/json')

    def test_get_category_products(self):
        cat = self.db.categories.find_one({'name_slug': 'cat-0'})
        products = list(
            self.db.products.find(
                {'cat_id': cat['_id']},
                sort=[('name', 1)],
                limit=app.PRODUCTS_PER_PAGE))
        for prod in products:
            prod['_id'] = str(prod['_id'])
            del prod['cat_id']

        self.assertEqual(
            json.loads(
                app.get_products_by_category('cat-0')),
            products)

    def get_product_details_request(self):
        req = self.app.get('/api/product/prod-0-0')
        self.assertEqual(req.status, '200 OK')
        self.assertEqual(req.content_type, 'application/json')

    def test_get_not_existing_product_details_request(self):
        req = self.app.get('/api/product/somekindofproduct')
        self.assertEqual(json.loads(req.body), [])

    def test_get_product_details(self):
        prod_0_0 = self.db.products.find_one({'name_slug': 'prod-0-0'})
        prod_0_0['_id'] = str(prod_0_0['_id'])
        del prod_0_0['cat_id']
        self.assertEqual(json.loads(app.get_product('prod-0-0')), prod_0_0)

    def test_add_product_to_basket(self):
        prod = self.db.products.find_one({'name_slug': 'prod-0-0'})
        req = self.app.post_json(
            '/api/basket/add',
            {'prod_id': str(prod['_id']), 'amount': 2})

        req_data = json.loads(req.body)

        self.assertEqual(req.status, '200 OK')
        self.assertIn('_id', req_data)
        self.assertEqual(req_data['total'], 2 * prod['price'])

        prod = self.db.products.find_one({'name_slug': 'prod-1-0'})
        req = self.app.post_json(
            '/api/basket/add',
            {'basket_id': req_data['_id'], 'prod_id': str(prod['_id']), 'amount': 4})
        req_data = json.loads(req.body)

        self.assertEqual(req.status, '200 OK')
        self.assertEqual(len(req_data['products']), 2)


if __name__ == '__main__':
    unittest.main()
