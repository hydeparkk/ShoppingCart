__author__ = 'hydeparkk'

from random import randint, random
import unittest

from pymongo import MongoClient

import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = MongoClient()
        self.db = self.client['shopping-cart-test']
        # Populate database with random data
        for i in xrange(randint(1, 10)):
            cat_id = self.db.categories.insert({'name': 'Cat%d' % i})
            for j in xrange(randint(1, 25)):
                price = random() * randint(1, 100)
                self.db.products.insert(
                    {'name': 'Prod%d' % j,
                     'price': round(price, 2),
                     'promo_price': round(price * 0.25, 2),
                     'category': cat_id})

    def tearDown(self):
        pass  # self.client.drop_database('shopping-cart-test')

    def test_get_categories(self):
        categories = app.get_categories()
        self.assertEqual(len(categories), self.db.categories.count())


if __name__ == '__main__':
    unittest.main()
