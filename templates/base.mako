<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><%block name="title"></%block></title>
    <link rel="stylesheet" type="text/css" href="/static/css/bootstrap.min.css" />
    <link rel="stylesheet" type="text/css" href="/static/css/app.css" />
</head>
<body>
    <div class="container body-content">
        <div class="page-header">
            <a href="/">
                <h1>Simple shopping cart <small>Have fun, be careful.</small></h1>
            </a>
        </div>
    <%block name="content"></%block>
    </div>
    <script src="/static/scripts/jquery-1.10.2.min.js"></script>
    <script src="/static/scripts/bootstrap.min.js"></script>
</body>
</html>