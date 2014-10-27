<%inherit file="templates/base.mako" />
<%block name="title">${prod['name']} - Product details</%block>

<%block name="content">
    <div class="row">
        <h3>${prod['name']}</h3>
        <h2>Details</h2>
    </div>
    <div class="row">
        <h3>Gallery</h3>
        % for i in range(5):
        <div class="col-sm-2">
            <div class="thumbnail">
                <img src="http://placehold.it/150x150">
            </div>
        </div>
        % endfor
    </div>
</%block>