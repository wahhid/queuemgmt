$(document).ready(function () {

    $('.sidebar-menu').tree();

    $('.btnpickup').click(function(e){
        pickup_id = $('.pickup-id').text();
        $.getJSON('/queue/pickup/' + pickup_id + '/', function (data) {
        })
        .done(function(data){
            json = JSON.stringify(data);
            console.log(json.counter_name)
            $('#counter_name').text(json.counter_name);
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    });

    $('.btnfinish').click(function(e){

    });
});