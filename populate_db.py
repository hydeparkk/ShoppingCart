__author__ = 'pjonski'

from random import randint, random

from pymongo import MongoClient

from app import slugify


def populate_db(database, host='localhost', port=27017):
    """

    :param database:
    :param host:
    :param port:
    """
    db = MongoClient(host=host, port=port)[database]
    for i in xrange(randint(5, 15)):
        cat_id = db.categories.insert(
            {'name': 'Cat_%d' % i, 'name_slug': slugify('Cat_%d' % i)})
        for j in xrange(randint(25, 100)):
            price = random() * randint(1, 100)
            db.products.insert(
                {'name': 'Prod_%d_%d' % (i, j),
                 'name_slug': slugify('Prod_%d_%d' % (i, j)),
                 'price': float('{0:.2f}'.format(price)),
                 'promo_price': float('{0:.2f}'.format(price * 0.75)),
                 'cat_id': cat_id})

    promo_codes = [
        {'code': 'hydecode', 'bonus': '20%'},
        {'code': 'testcode', 'bonus': '100'},
        {'code': 'free', 'bonus': '100%'}
    ]

    db.promo_codes.insert(promo_codes)

if __name__ == '__main__':
    populate_db('shopping-cart')
