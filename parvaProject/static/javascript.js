function createGame() {
    $(".log").html("Creating Game");
    $.post("madn-endpoint/", {
        createGame: 1 + $(".options").serializeArray()
    })
    .done(function (response) {
        $(".log").html(response);
    });
    $('.joinGame').remove();
    $('.createGame').attr('onclick' , 'startGame()');
    $('.createGame').text('Start Game');
}

function startGame(){
    $('.createGame').remove();
    $(".log").html("Please Dice its your turn");
    $(".dice").toggle();
}

function joinGame() {
    $(".log").html("Connecting to Server");
    $.post("madn-endpoint/", {
        joinGame: 1
    })
    .done(function (response) {
        $(".log").html(response);
    });
    $('.joinGame').remove();
    $('.createGame').remove();
}

function getStatus() {
    $.post("madn-endpoint/", {
        getStatus: 1
    })
    .done(function (response) {
        var status = JSON.parse(response);
        $(".status").html("");
        var names =  ["turn", "diced", "rank", "players"];
        for(index = 0; index < 4; index++){
            Cookies.set(names[index], status[index]);
            $(".status").append(names[index] + " : " + status[index] + "</br>");
        }
        var playground = [];
        for(index = 4; index < status.length; index++){
            playground.push(status[index]);
        }
        $.each(playground, function(indexx, line){
            $.each(line, function(indexy, value) {
                if (value !== '-') {
                    $('[id="' + indexx + '' + indexy + '"]').html("</br>" + value);
                }
            });
        });
        Cookies.set('playgound', JSON.stringify(playground));
        /**
         * var json_str = getCookie('mycookie');
var arr = JSON.parse(json_str);
         */
    });
}

function dice() {
    if(Cookies.get('rank') === Cookies.get('turn')){
        var faceValue, output = '';

        faceValue = Math.floor(Math.random() * 6);
        output += "&#x268" + faceValue + "; ";

        document.getElementById('dice').innerHTML = output;
        $.post("madn-endpoint/", {
            dice: faceValue+1
        })
        .done(function (response) {
            $(".log").html(response);
        });
    }
}
setInterval(function() {
    update()
}, 5000);

function update(){
    getStatus();
    if(Cookies.get('player')>1){
        $('.createGame').attr('onclick' , 'startGame()');
        $('.createGame').text('Start Game');
        $('.joinGame').remove();
    }
    if(Cookies.get('rank') > 0){
        $('.createGame').remove();
    }
}
$(document).ready(function () {
    update();
    /*for (var i = 0; i <= 10; i++) {
        for (var j = 0; j <= 10; j++) {
            $('.content').append("<div id='"+i+""+j+"' class='coord'></div>");
        }
        $('.content').append("<div class='w-100'></div>");
    }*/
    /*var test = "[";
    for (var i = 0; i <= 9; i++) {
        for (var j = 0; j <= 9; j++) {
            test+="-, ";
        }
        test+="['-']][";
    }
    test+="['-']]";
    console.log(test);*/
});
/*$(document).ready(function () {
    var overIndex = 0;
    function functionToLoadFile() {
        jQuery.get('static/log.txt', function (data) {
            var split = data.split(/\n/);
            console.log(split);
            console.log(overIndex);

            for (var i =overIndex; i < split.length; i++) {
                $('.content').append('<p>'+split[i]+'</p>');
            }

            $('.content').scrollTop($('.content')[0].scrollHeight);

            overIndex = split.length;

            setTimeout(functionToLoadFile, 5000);
        });
    }

    setTimeout(functionToLoadFile, 10);
});*/