__author__ = 'hydeparkk'

import json
from random import randint
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
        # Add basket for testing purposes
        # add some products to basket
        prod = self.db.products.find_one({'name_slug': 'prod-0-0'})
        req = self.app.post_json(
            '/api/basket/add',
            {'prod_id': str(prod['_id']), 'amount': 4}
        )
        for prod in self.db.products.find(skip=1, limit=5):
            req = self.app.post_json(
                '/api/basket/add',
                {'basket_id': json.loads(req.body)['_id'], 'prod_id': str(
                    prod['_id']), 'amount': randint(1, 10)}
            )

        self.basket = json.loads(req.body)

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
        self.assertEqual(len(req_data['products']), 1)

    def test_add_existing_product_to_basket(self):
        prod = self.db.products.find_one({'name_slug': 'prod-0-0'})
        req = self.app.post_json(
            '/api/basket/add',
            {'prod_id': str(prod['_id']), 'amount': 2}
        )

        req_data = json.loads(req.body)

        sec_req = self.app.post_json(
            '/api/basket/add',
            {'basket_id': req_data['_id'],
             'prod_id': str(prod['_id']),
             'amount': 3}
        )

        sec_req_data = json.loads(sec_req.body)
        self.assertEqual(
            sec_req_data['products'][0]['price'], prod['promo_price'])
        self.assertEqual(sec_req_data['products'][0]['amount'], 5)

    def test_remove_product_from_basket(self):
        req = self.app.delete_json(
            '/api/basket/remove',
            {
                'basket_id': self.basket['_id'],
                'prod_id': str(self.basket['products'][0]['prod_id'])
            }
        )

        self.assertEqual(len(json.loads(req.body)['products']), 5)

    def test_add_promo_code_to_basket(self):
        req = self.app.post_json(
            '/api/basket/promocode',
            {
                'basket_id': self.basket['_id'],
                'promo_code': 'hydecode'
            }
        )
        req_data = json.loads(req.body)

        self.assertEqual(len(req_data['promo_codes']), 1)

    def test_add__not_existing_promo_code_to_basket(self):
        req = self.app.post_json(
            '/api/basket/promocode',
            {
                'basket_id': self.basket['_id'],
                'promo_code': 'qwerty'
            }
        )
        req_data = json.loads(req.body)

        self.assertEqual(req_data, [])

if __name__ == '__main__':
    unittest.main()
