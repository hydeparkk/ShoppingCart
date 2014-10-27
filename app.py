__author__ = 'hydeparkk'

from os import path
import json

from bottle import Bottle, static_file, response, run, mako_template
from pymongo import MongoClient


SITE_ROOT = path.dirname(__file__)
PRODUCTS_PER_PAGE = 12

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
    cat_id = db.categories.find_one({'name_slug': cat_name})['_id']
    products = list(
        db.products.find(
            {'cat_id': cat_id},
            sort=[('name', 1)],
            skip=page * PRODUCTS_PER_PAGE,
            limit=(page + 1) * PRODUCTS_PER_PAGE))

    for prod in products:
        prod['_id'] = str(prod['_id'])
        del prod['cat_id']

    response.content_type = 'application/json'
    return json.dumps(products)


@shopping_cart_app.route('/api/product/<prod_name>')
def get_product(prod_name):
    prod = db.products.find_one({'name_slug': prod_name})
    prod['_id'] = str(prod['_id'])
    del prod['cat_id']

    response.content_type = 'application/json'
    return json.dumps(prod)

@shopping_cart_app.route('/api/basket/add', method='POST')
def add_product_to_basket():
    if '' == 'new':
        pass
    else:
        pass


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
