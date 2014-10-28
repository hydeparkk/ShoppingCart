__author__ = 'hydeparkk'

from os import path
import json

from bottle import Bottle, static_file, response, run, mako_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId


SITE_ROOT = path.dirname(__file__)
PRODUCTS_PER_PAGE = 30

db = MongoClient()['shopping-cart']
db.categories.ensure_index([('name', 1), ('unique', True), ('dropDups', True)])
db.products.ensure_index([('name', 1), ('unique', True), ('dropDups', True)])
shopping_cart_app = Bottle()


def slugify(text):
    from unicodedata import normalize

    allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789-'
    if isinstance(text, str):
        text = text.decode('ascii')
    clean_text = text.strip().replace(' ', '-').lower()
    clean_text = clean_text.replace('_', '-')
    while '--' in clean_text:
        clean_text = clean_text.replace('--', '-')
    ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
    strict_text = map(lambda x: x if x in allowed_chars else '', ascii_text)
    return ''.join(strict_text)


# ---------------------------------------
# Static route
# ---------------------------------------
@shopping_cart_app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=path.join(SITE_ROOT, 'static'))


# ---------------------------------------
# API routes
# ---------------------------------------
@shopping_cart_app.route('/api/category')
def get_categories():
    ret_val = []
    for cat in db.categories.find(sort=[('name', 1)]):
        ret_val.append(
            {'name': cat['name'],
             'name_slug': cat['name_slug'],
             'prod_amount': db.products.find({'cat_id': cat['_id']}).count()})

    response.content_type = 'application/json'
    return json.dumps(ret_val)


@shopping_cart_app.route('/api/category/<cat_name>')
@shopping_cart_app.route('/api/category/<cat_name>/<page:int>')
def get_products_by_category(cat_name, page=0):
    response.content_type = 'application/json'
    try:
        cat_id = db.categories.find_one({'name_slug': cat_name})['_id']
    except TypeError:
        return json.dumps([])
    products = list(
        db.products.find(
            {'cat_id': cat_id},
            sort=[('name', 1)],
            skip=page * PRODUCTS_PER_PAGE,
            limit=(page + 1) * PRODUCTS_PER_PAGE))

    for prod in products:
        prod['_id'] = str(prod['_id'])
        del prod['cat_id']

    return json.dumps(products)


@shopping_cart_app.route('/api/product/<prod_name>')
def get_product(prod_name):
    response.content_type = 'application/json'
    prod = db.products.find_one({'name_slug': prod_name})
    if prod is not None:
        prod['_id'] = str(prod['_id'])
        del prod['cat_id']

        return json.dumps(prod)
    else:
        return json.dumps([])


@shopping_cart_app.route('/api/basket/add', method='POST')
def add_product_to_basket():
    data = request.json
    prod = db.products.find_one({'_id': ObjectId(data['prod_id'])})
    price = prod['price'] if data['amount'] < 3 else prod['promo_price']

    if 'basket_id' in data:
        basket = db.basket.find_one({'_id': ObjectId(data['basket_id'])})
        if data['prod_id'] in [item['prod_id']for item in basket['products']]:
            for item in basket['products']:
                if item['prod_id'] == data['prod_id']:
                    item['amount'] += data['amount']
                    if item['amount'] > 2:
                        item['price'] = prod['promo_price']

            total = sum([item['amount'] * item['price']
                         for item in basket['products']])

            db.basket.update(
                {
                    '_id': ObjectId(data['basket_id']),
                    'products.prod_id': data['prod_id']
                },
                {
                    '$set': {'total': round(total, 2)},
                    '$push': {
                        'products.$': {
                            'price': price,
                            'amount': data['amount']
                        }
                    }
                }
            )
        else:
            total = basket['total'] + price * data['amount']
            ret = db.basket.update(
                {'_id': ObjectId(data['basket_id'])},
                {
                    '$set': {'total': round(total, 2)},
                    '$push': {
                        'products': {
                            'prod_id': data['prod_id'],
                            'price': price,
                            'amount': data['amount']
                        }
                    }
                }
            )
            print(ret)
    else:
        basket = db.basket.insert(
            {
                'products': [
                    {
                        'prod_id': data['prod_id'],
                        'price': price,
                        'amount': data['amount']
                    }
                ],
                'promo_codes': [],
                'total': round(price * data['amount'], 2),
            }
        )

    if isinstance(basket, ObjectId):
        basket = db.basket.find_one({'_id': basket})
    else:
        basket = db.basket.find_one({'_id': ObjectId(data['basket_id'])})

    basket['_id'] = str(basket['_id'])
    response.content_type = 'application/json'
    return json.dumps(basket)


# ---------------------------------------
# WebPage routes
# ---------------------------------------
@shopping_cart_app.route('/')
def index():
    return mako_template('templates\\categories.mako',
                         cats=json.loads(get_categories()))


@shopping_cart_app.route('/category/<cat_name>')
@shopping_cart_app.route('/category/<cat_name>/<page:int>')
def category_products(cat_name, page=0):
    return mako_template('templates\\products.mako',
                         prods=json.loads(
                             get_products_by_category(cat_name, page)),
                         cat=db.categories.find_one({'name_slug': cat_name}))


@shopping_cart_app.route('/product/<prod_name>')
def product_details(prod_name):
    return mako_template('templates\\product.mako',
                         prod=json.loads(get_product(prod_name)))


if __name__ == '__main__':
    run(shopping_cart_app,
        host='0.0.0.0',
        port=8000,
        reloader=True,
        debug=True)
