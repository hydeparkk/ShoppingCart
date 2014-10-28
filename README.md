Shopping cart module
====================

### Functionality:
1. It's possible to return list of all categories of products together with count of products per category
2. It's possible to return short list (only few product fields) of all products in specified category
3. It's possible to return detailed information about product like id, name, price, price in promotion (buy 3 of those and you will get X$ discount)
4. It's possible to add items to basket
5. It's possible to apply discount coupon to existing basket
6. It's possible to remove items from basket
 
### Must have requirements:
* Application must work (just let us know how to run it)
* Define rest api for entire module and stub functionality
* Implement at least one functionality specified above from end-to-end in TDD (assuming that MongoDB runs on default port - 27017)

___

How to run it?
--------------

Create a virtualenv, activate it and install all necessary modules: 

    > virtualenv shoppingcart
    > shoppingcart/scripts/activate.bat
    > cd <project_root_directory>
    > pip install -r requirements.txt

Populate database with data using `populate_db.py` script. 
