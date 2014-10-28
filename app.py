__author__ = 'hydeparkk'

from os import path
import json

from bottle import app, static_file, response, run, mako_template, request, route, hook
from pymongo import MongoClient
from bson.objectid import ObjectId
from beaker.middleware import SessionMiddleware


session_opts = {
    'session.type': 'file',
    'session.data_dir': './session',
    'session.auto': True
}

SITE_ROOT = path.dirname(__file__)
PRODUCTS_PER_PAGE = 30

db = MongoClient()['shopping-cart']
db.categories.ensure_index([('name', 1), ('unique', True), ('dropDups', True)])
db.products.ensure_index([('name', 1), ('unique', True), ('dropDups', True)])

shopping_cart_app = SessionMiddleware(app(), session_opts)


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


@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


# ---------------------------------------
# Static route
# ---------------------------------------
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=path.join(SITE_ROOT, 'static'))


# ---------------------------------------
# API routes
# ---------------------------------------
@route('/api/category')
def get_categories():
    ret_val = []
    for cat in db.categories.find(sort=[('name', 1)]):
        ret_val.append(
            {'name': cat['name'],
             'name_slug': cat['name_slug'],
             'prod_amount': db.products.find({'cat_id': cat['_id']}).count()})

    response.content_type = 'application/json'
    return json.dumps(ret_val)


@route('/api/category/<cat_name>')
@route('/api/category/<cat_name>/<page:int>')
def get_products_by_category(cat_name, page=1):
    response.content_type = 'application/json'
    try:
        cat_id = db.categories.find_one({'name_slug': cat_name})['_id']
    except TypeError:
        return json.dumps([])
    products = list(
        db.products.find(
            {'cat_id': cat_id},
            sort=[('name', 1)],
            skip=(page - 1) * PRODUCTS_PER_PAGE,
            limit=page * PRODUCTS_PER_PAGE))

    for prod in products:
        prod['_id'] = str(prod['_id'])
        del prod['cat_id']

    return json.dumps(products)


@route('/api/product/<prod_name>')
def get_product(prod_name):
    response.content_type = 'application/json'
    prod = db.products.find_one({'name_slug': prod_name})
    if prod is not None:
        prod['_id'] = str(prod['_id'])
        del prod['cat_id']

        return json.dumps(prod)
    else:
        return json.dumps([])


@route('/api/basket/add', method='POST')
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
                    amount = item['amount']
                    if item['amount'] > 2:
                        price = prod['promo_price']
                        item['price'] = price

            db.basket.update(
                {
                    '_id': ObjectId(data['basket_id']),
                    'products.prod_id': data['prod_id']
                },
                {
                    '$set': {
                        'products.$': {
                            'prod_id': data['prod_id'],
                            'price': price,
                            'amount': amount
                        }
                    }
                }
            )
        else:
            db.basket.update(
                {'_id': ObjectId(data['basket_id'])},
                {
                    '$push': {
                        'products': {
                            'prod_id': data['prod_id'],
                            'price': price,
                            'amount': data['amount']
                        }
                    }
                }
            )
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
            }
        )
        request.session['basket_id'] = str(basket)

    if isinstance(basket, ObjectId):
        basket = db.basket.find_one({'_id': basket})
    else:
        basket = db.basket.find_one({'_id': ObjectId(data['basket_id'])})

    basket['_id'] = str(basket['_id'])
    response.content_type = 'application/json'
    return json.dumps(basket)


@route('/api/basket/remove', method='DELETE')
def remove_product_from_basket():
    response.content_type = 'application/json'
    data = request.json
    if 'basket_id' in data:
        db.basket.update(
            {'_id': ObjectId(data['basket_id'])},
            {
                '$pull':
                {
                    'products':
                    {
                        'prod_id': data['prod_id']
                    }
                }
            }
        )
        basket = db.basket.find_one({'_id': ObjectId(data['basket_id'])})
        basket['_id'] = str(basket['_id'])
        return json.dumps(basket)
    else:
        return json.dumps([])


@route('/api/basket/promocode', method='POST')
def add_promo_code():
    response.content_type = 'application/json'
    data = request.json
    if 'basket_id' in data:
        basket = db.basket.find_one({'_id': ObjectId(data['basket_id'])})
        if data['promo_code'] not in [item['promo_code']
                                      for item in basket['promo_codes']]:
            promo_code = db.promo_codes.find_one({'code': data['promo_code']})
            if promo_code is not None:
                db.basket.update(
                    {'_id': basket['_id']},
                    {
                        '$push':
                        {
                            'promo_codes':
                            {
                                'promo_code': promo_code['code'],
                                'bonus': promo_code['bonus']
                            }
                        }
                    }
                )
                basket = db.basket.find_one(
                    {'_id': ObjectId(data['basket_id'])})
                basket['_id'] = str(basket['_id'])
                return json.dumps(basket)

    return json.dumps([])


# ---------------------------------------
# WebPage routes
# ---------------------------------------
@route('/')
def index():
    cats = json.loads(get_categories())
    response.content_type = 'text/html'
    return mako_template('templates\\categories.mako',
                         cats=cats)


@route('/category/<cat_name>')
@route('/category/<cat_name>/<page:int>')
def category_products(cat_name, page=1):
    prods = json.loads(get_products_by_category(cat_name, page))
    cat = db.categories.find_one({'name_slug': cat_name})
    pages = db.products.find(
        {'cat_id': cat['_id']}).count() / PRODUCTS_PER_PAGE + 2
    response.content_type = 'text/html'
    return mako_template('templates\\products.mako',
                         prods=prods,
                         cat=cat,
                         pages=pages)


@route('/product/<prod_name>')
def product_details(prod_name):
    prod = json.loads(get_product(prod_name))
    response.content_type = 'text/html'
    return mako_template('templates\\product.mako',
                         prod=prod,
                         basket_id=request.session.get('basket_id', None))


@route('/basket')
def get_basket():
    basket = db.basket.find_one(
        {'_id': ObjectId(request.session.get('basket_id', None))})
    if basket is not None:
        total = 0
        for prod in basket['products']:
            prd = db.products.find_one({'_id': ObjectId(prod['prod_id'])})
            prod['name'] = prd['name']
            prod['slug'] = prd['name_slug']
            total += prod['amount'] * prod['price']

        tmp = 0
        for code in basket['promo_codes']:
            if '%' in code['bonus']:
                tmp = total * \
                    (1 - (int(code['bonus'].replace('%', '')) / 100.0))
                total *= 1 - (int(code['bonus'].replace('%', '')) / 100.0)
            else:
                total -= int(code['bonus'])

        basket['total'] = total if total > 0 else 0
    return mako_template('templates\\basket.mako',
                         basket=basket)


if __name__ == '__main__':
    run(shopping_cart_app,
        host='0.0.0.0',
        port=8000,
        reloader=True,
        debug=True)
