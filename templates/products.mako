<%inherit file="templates/base.mako" />
<%block name="title">${cat['name']} - Products list</%block>

<%block name="content">
    <div class="row">
        %for prod in prods:
        <div class="col-md-2">
            <div class="thumbnail">
                <a href="/product/${prod['name_slug']}}">
                    <img src="http://placehold.it/150x150">
                </a>
                <div class="caption">
                    <a href="/product/${prod['name_slug']}">${prod['name']}</a>
                </div>
            </div>
        </div>
        %endfor
    </div>
</%block>