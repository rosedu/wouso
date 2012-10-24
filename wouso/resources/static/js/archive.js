
var url_base = '';

/* Emoticons and the replace function. */
var emoticons = {
    '>:D':'emoticon_evilgrin.png',
    ':D':'emoticon_grin.png',
    '=D':'emoticon_happy.png',
    ':\\)':'emoticon_smile.png',
    ':O':'emoticon_surprised.png',
    ':P':'emoticon_tongue.png',
    ':\\(':'emoticon_unhappy.png',
    ';\\)':'emoticon_wink.png',
    '\\(ball\\)':'sport_soccer.png'
};

var img_dir = url_base + "/static/img/";
function replace_emoticons(text) {
    $.each(emoticons, function (character, img) {
        var re = new RegExp(character, 'g');
        text = text.replace(re, '<img src="' + img_dir + img + '" />');
    });
    return text;
}


$(function() {
    $('#datepicker').datepicker();
    $('#datepicker_private').datepicker();
    $('#slider').slider({
        range: true,
        max:24,
        values: [0, 24]

    });
    $("#slider").bind( "slidechange", function(event, ui) {
        var x = $("#slider").slider("values");
        $("#minSlider").html(x[0]);
        $("#maxSlider").html(x[1]);
    })


});


$(document).ready(function(){

    $.ajaxSetup({
        beforeSend:function (xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    $("#archive_day").click(function(){
        var date = $("#datepicker").val();
        if(date){
            date = date + "/" + $("#minSlider").html();
            var hours = $("#maxSlider").html() - $("#minSlider").html();
            msgdata = {'room':'global', 'date':date, 'hours':hours};
            var args = {type:"POST", url:url_base + "/chat/archive_messages/", data:msgdata, complete:printArchive};
            $.ajax(args);
        }
    });

    function printArchive(res, status){
        if(status == "success"){
            $("#global_area").html("");
            var obj = jQuery.parseJSON(res.responseText);
            var i;
            for(i = 0; i < obj.count; i++){
                $('#global_area').append(obj.msgs[i].time + obj.msgs[i].user + ": " + replace_emoticons(obj.msgs[i].text) + "<br>");
            }
        }
    }

    $("#archive_day_private").click(function(){
        var id = $("#to").val();
        if(id && id!=myID){
            var msgdata = {'opcode':'getRoom', 'from':myID, 'to':id, 'time': timeStamp};
            var args = {type:"POST", url:url_base + "/chat/chat_m/", data:msgdata, complete:getRoom};
            $.ajax(args);
        }
    });

    function getRoom(res, status){
        if(status == "success"){
            var obj = $.parseJSON(res.responseText);
            var chat_room = obj.name;
            var date = $("#datepicker_private").val();
            if(date){
                msgdata = {'room':chat_room,'date':date};
                var args = {type:"POST", url:url_base + "/chat/archive_messages/", data:msgdata, complete:printArchive_private};
                $.ajax(args);
            }
        }
    }

    function printArchive_private(res, status){
        if(status == "success"){
            $("#private_area").html("");
            var obj = jQuery.parseJSON(res.responseText);
            var i;
            for(i = 0; i < obj.count; i++){
                $('#private_area').append(obj.msgs[i].time + obj.msgs[i].user + ": " + replace_emoticons(obj.msgs[i].text) + "<br>");
            }
        }
    }

});
