$(document).ready(function () {
    $('#buy').click(function () {
        var data = {};
        data.prod_id = $(this).attr('data-prod-id')
        data.amount = parseInt($('#amount').val());
        if ($(this).attr('data-basket-id') != 'None') {
            data.basket_id = $(this).attr('data-basket-id');
        }
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            url: '/api/basket/add',
            success: function () {
                alert('Product added to basket!');
            }
        });
    });

    $('.remove-from-basket').click(function () {
        var data = {};
        data.prod_id = $(this).attr('data-prod-id');
        data.basket_id = $(this).attr('data-basket-id');
        $.ajax({
            type: 'DELETE',
            contentType: 'application/json',
            data: JSON.stringify(data),
            url: '/api/basket/remove',
            success: function () {
                location.reload();
            }
        });
    });

    $('#add-promo-code').click(function () {
        var data = {};
        data.promo_code = $('#promo-code').val();
        data.basket_id = $(this).attr('data-basket-id');
        console.log(data);
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            url: '/api/basket/promocode',
            success: function () {
                location.reload();
            }
        });
    });
});