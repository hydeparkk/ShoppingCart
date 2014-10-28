<%inherit file="templates/base.mako" />
<%block name="title">${cat['name']} - Products list</%block>

<%block name="content">
    <div class="row">
        % for prod in prods:
        <div class="col-md-2">
            <div class="thumbnail">
                <a href="/product/${prod['name_slug']}">
                    <img src="http://placehold.it/150x150">
                </a>
                <div class="caption">
                    <a href="/product/${prod['name_slug']}">${prod['name']}</a>
                    <span class="label label-primary pull-right"><span class="glyphicon glyphicon-usd"></span> ${prod['price']}</span>
                </div>
            </div>
        </div>
        % endfor
    </div>
    % if pages > 2:
    <div class="row">
        <div class="col-md-pull-4"></div>
        <div class="col-md-4">
            <ul class="pagination center-block">
                % for page in xrange(1, pages):
                <li><a href="/category/${cat['name_slug']}/${page}">${page}</a></li>
                % endfor
            </ul>
        </div>
    </div>
    % endif
</%block>