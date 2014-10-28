<%inherit file="templates/base.mako" />
<%block name="title">Basket</%block>

<%block name="content">
    <div class="row">
        % if basket is not None and len(basket['products']) > 0:
            <div class="col-md-8">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Amount</th>
                            <th>Price</th>
                            <th>Sum</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        % for prod in basket['products']:
                        <tr>
                            <td><a class="btn btn-link" href="/product/${prod['slug']}">${prod['name']}</a></td>
                            <td>${prod['amount']}</td>
                            <td>${prod['price']}</td>
                            <td>${prod['price'] * prod['amount']}</td>
                            <td><button class="btn btn-sm remove-from-basket" data-prod-id="${prod['prod_id']}" data-basket-id="${basket['_id']}"><span class="glyphicon glyphicon-remove text-danger"></span></button></td>
                        </tr>
                        % endfor
                        <tr>
                            <td colspan="3"></td>
                            <td>${basket['total']}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="col-md-4">
                <div class="panel panel-info">
                    <div class="panel-heading">Used promo codes</div>
                    <div class="panel-body">
                    % if basket['promo_codes']:
                    % for code in basket['promo_codes']:
                        <p>${code['promo_code']} <span class="label label-success pull-right">-${code['bonus']}</span></p>
                    % endfor
                    % endif
                        <div class="form-inline">
                            <input id="promo-code" class="form-control" type="text" placeholder="Enter promo code"/>
                            <button id="add-promo-code" class="btn btn-primary" data-basket-id="${basket['_id']}">Add</button>
                        </div>
                    </div>
                </div>
            </div>
        % else:
            <h2>Your basket is empty.</h2>
        % endif
    </div>
</%block>