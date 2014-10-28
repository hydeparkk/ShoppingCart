<%inherit file="templates/base.mako" />
<%block name="title">${prod['name']} - Product details</%block>

<%block name="content">
    <div class="row">
        <div class="col-md-4">
            <h3>${prod['name']}</h3>
            <div class="form-inline">
                <input id="amount" class="form-control" value="1" min="1" max="999" type="number" pattern="[1-9][0-9]{2}" name="amount" />
                <button id="buy" class="btn btn-primary form-control" data-prod-id="${prod['_id']}" data-basket-id="${basket_id}">Buy</button>
            </div>
        </div>
        <div class="col-md-4">
            <h4 class="text-info">Details</h4>
            <table class="table">
                <tr>
                    <td>Price:</td>
                    <td>${prod['price']}</td>
                </tr>
                <tr>
                    <td>Promo Price: <span class="text-warning">*</span></td>
                    <td>${prod['promo_price']}</td>
                </tr>
            </table>
            <p class="text-warning">*To get promo price buy 3 or more.</p>
        </div>
    </div>
    <div class="row">
        <h4 class="text-info">Gallery</h4>
        % for i in range(5):
        <div class="col-sm-2">
            <div class="thumbnail">
                <img src="http://placehold.it/150x150">
            </div>
        </div>
        % endfor
    </div>
</%block>