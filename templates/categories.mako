<%inherit file="templates/base.mako" />
<%block name="title">Categories</%block>

<%block name="content">
    % for cat in cats:
        <div class="col-md-4">
            <div class="media">
                <a class="pull-left" href="">
                    <img class="media-object" src="http://placehold.it/100x100">
                </a>
                <div class="media-body">
                    <div class="media-heading">
                        <h4>
                            <a href="/category/${cat['name_slug']}">${cat['name']}</a>
                        </h4>
                        <p>Products: <span class="badge">${cat['prod_amount']}</span></p>
                    </div>
                </div>
            </div>
        </div>
    % endfor
</%block>