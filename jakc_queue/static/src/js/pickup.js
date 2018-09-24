$(document).ready(function () {

    $('.sidebar-menu').tree();

    $('button').on('click', function (e){
       //console.log('click');
       //alert($(this).attr('code'));
       if($(this).attr('code') === 'pickup'){
            pickup_id = $('.pickup-id').text().trim();
            pickupQueue(pickup_id)
       }
    });

    function pickupQueue(id){
        console.log("pickup");
        console.log(id);
        $.getJSON('/queue/pickup/' + id + '/', function (data) {
        })
        .done(function(data){
            console.log(data);
            console.log(data.counter_name)
            $('#counter_name').text(data.counter_name);
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

});