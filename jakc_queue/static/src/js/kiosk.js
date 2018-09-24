$(document).ready(function () {
    $('.sidebar-menu').tree();
    //Loading Counter
    //setInterval(loadCounter, 1000);
    //Loading Queuing
    //setInterval(loadQueue, 1000);

    function loadCounter(){
        //$.getJSON('static/src/json/counter.json', function (data) {
        $.getJSON('/queue/type/listall', function (data) {
        })
        .done(function(data){
            json = JSON.stringify(data);
            $('#counter-grid').empty();
            $.each( json.data, function( i, item ) {
                 var html = '<div class="col-md-12 col-xs-12">' +
                            '   <button id="btn" type="button" code="' + item.counter_id + '" class="btn3d btn btn-danger btn-lg btn-block" style="font-size:58px;">' +
                            '       <span class="info-box-icon"><i id="btn" class="fa ' + item.counter_fa + '"></i></span> ' +  item.counter_name +
                            '   </button>' +
                            '</div>'
                $('#counter-grid').append(html);
            });
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    $('button').on('click', function (e){
       //console.log('click');
       //alert($(this).attr('code'));
       createQueue($(this).attr('code'));
    });

    function createQueue(code){
         console.log( "Create Queue");
         $.ajax({
            url         : "/queue/kiosk/request/" + code + "/",
            type        : "POST",
            data        : {
            },
            dataType    : "json",
            success     : function(resp) {
                console.log(resp);
                $('#counter_name').text(resp.counter_name);
                $('#counter_trans').text(resp.counter_trans);
            },
            error        : function(xhr, status, error){
                alert(xhr);
            }
        });
    }
});

