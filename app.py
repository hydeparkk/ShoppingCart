__author__ = 'hydeparkk'

from os import path

from bottle import Bottle, static_file, run
from pymongo import MongoClient

SITE_ROOT = path.dirname(__file__)

db = MongoClient()['shopping-cart']
shopping_cart_app = Bottle()


@shopping_cart_app.route('/static/<filepath:path>')
def server_static(filename):
    return static_file(filename, root=path.join(SITE_ROOT, 'static'))

@shopping_cart_app.route('/api/category', method='GET')
def get_categories():
    pass

if __name__ == '__main__':
    run(shopping_cart_app, host='0.0.0.0', port=8000, reloader=True, debug=True)