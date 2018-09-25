
  $(document).ready(function () {
    $('.sidebar-menu').tree();

    //Loading Counter
    setInterval(loadCounter, 1000);
    //Loading Queuing
    setInterval(loadQueue, 1000);
    //Loading Sound
    setInterval(loadSound, 1000);


    function loadCounter(){
        //$.getJSON('static/src/json/counter.json', function (data) {
        $.getJSON('/queue/routeui/listactive/1', function (data) {

        })
        .done(function(data){
            $('#counter-grid').empty();
            $.each( data, function( i, item ) {
                console.log(item.counter_name);
                console.log(item.current_trans);
                var html =  '<div class="col-md-4 col-xs-12">' +
                            '<div class="box box-widget widget-user-2">' +
                            '   <div class="widget-user-header ' + item.counter_bg + '">' +
                            '       <div class="widget-user-image">' +
                            '           <span class="info-counter-icon ' + item.counter_bg + '"><i class="fa ' + item.counter_fa + '"></i></span>' +
                            '       </div>' +
                            '       <h3 class="widget-user-username">' + item.pickup_name + '</h3>' +
                            '       <h5 class="widget-user-desc" id="counter-desc-01">' + item.counter_name + '</h5>' +
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
        $.getJSON('/queue/routeui/listnew', function (data) {
        })
        .done(function(data){
            $('#queue-grid').empty();
            $.each( data, function( i, item ) {
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
                  if (i == 7){
                    return false;
                }
            });

        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    function loadSound(){
        console.log("Check Sound")
        //$.getJSON('static/src/json/counter.json', function (data) {
        $.getJSON('/queue/routeui/checksound/', function (data) {

        })
        .done(function(resp){
            console.log(resp);
            counter_trans = resp.counter_trans;
            counter_number = resp.counter_number;
            if (resp.status == true){
                console.log("Play Sound");
                file_names = [
                    '/jakc_queue/static/src/snd/nomor-urut.MP3',
                    '/jakc_queue/static/src/snd/' + counter_trans.charAt(0) + '.MP3',
                    '/jakc_queue/static/src/snd/' + counter_trans.charAt(1) + '.MP3',
                    '/jakc_queue/static/src/snd/' + counter_trans.charAt(2) + '.MP3',
                    '/jakc_queue/static/src/snd/konter.MP3',
                    '/jakc_queue/static/src/snd/' + counter_number + '.MP3',
                ]
                play_audio(file_names);
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log('getJSON request failed! ' + textStatus);
        });
    }

    function play_audio(file_names) {
        console.log(file_names)
        sound = new Howl({
            src: [file_names[0]],
            volume: 0.5,
            onend: function() {
                file_names.shift();
                if (file_names.length > 0) {
                    play_audio(file_names);
                }
            }
        });
        sound.play();
    }
  });
