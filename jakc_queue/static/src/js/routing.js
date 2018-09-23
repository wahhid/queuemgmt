
  $(document).ready(function () {
    $('.sidebar-menu').tree();
    //Loading Counter
    setInterval(loadCounter, 1000);
    //Loading Queuing
    setInterval(loadQueue, 1000);

    function loadCounter(){
        //$.getJSON('static/src/json/counter.json', function (data) {
        $.getJSON('/jakc_queue/static/src/json/counter.json', function (data) {

        })
        .done(function(data){
            $('#counter-grid').empty();
            $.each( data.data, function( i, item ) {
                console.log(item.counter_name);
                console.log(item.current_trans);
                var html =  '<div class="col-md-4 col-xs-12">' +
                            '<div class="box box-widget widget-user-2">' +
                            '   <div class="widget-user-header ' + item.counter_bg + '">' +
                            '       <div class="widget-user-image">' +
                            '           <span class="info-counter-icon ' + item.counter_bg + '"><i class="fa ' + item.counter_fa + '"></i></span>' +
                            '       </div>' +
                            '       <h3 class="widget-user-username">' + item.counter_name + '</h3>' +
                            '       <h5 class="widget-user-desc" id="counter-desc-01">' + item.counter_desc + '</h5>' +
                            '   </div>' +
                            '   <div class="box-footer no-padding">' +
                            '       <center>' +
                            '           <span class="badge ' + item.counter_bg +'" style="margin:20px;font-size:148px;">' + item.current_trans + '</span>' +
                            '       </center>' +
                            '   </div>' +
                            '</div>' +
                            '</div>';
                $('#counter-grid').append(html);
                if (i == 2){
                    return false;
                }
            });
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

     function loadQueue(){
        //$.getJSON('static/src/json/queue.json', function (data) {
        $.getJSON('/jakc_queue/static/src/json/queue.json', function (data) {
        })
        .done(function(data){
            $('#queue-grid').empty();
            $.each( data.data, function( i, item ) {
                console.log(item.counter_name);
                console.log(item.current_trans);
                var html  = '<div class="col-md-3 col-xs-12">' +
                            '   <div class="small-box ' + item.counter_bg + '">' +
                            '       <div class="inner">' +
                            '           <h3>' + item.current_trans + '</h3>' +
                            '           <p>' + item.counter_name + '</p>' +
                            '       </div>' +
                            '       <div class="icon">' +
                            '           <i class="ion ion-stats-bars"></i>' +
                            '       </div>' +
                            '           <a href="#" class="small-box-footer">' +
                            '           <i class="fa ' + item.counter_fa + '"></i>' +
                            '       </a>' +
                            '   </div>' +
                            '</div>';
                 $('#queue-grid').append(html);
            });

        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

  });
