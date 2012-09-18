
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

    $("#archive_day").click(function(){
        var date = $("#datepicker").val();
        if(date){
            date = date + "/" + $("#minSlider").html();
            var hours = $("#maxSlider").html() - $("#minSlider").html();
            msgdata = {'room':'global', 'date':date, 'hours':hours};
            var args = {type:"POST", url:"/chat/archive_messages/", data:msgdata, complete:printArchive};
            $.ajax(args);
        }
    });

    function printArchive(res, status){
        if(status == "success"){
            $("#global_area").html("");
            var obj = jQuery.parseJSON(res.responseText);
            var i;
            for(i = 0; i < obj.count; i++){
                $("#global_area").append(obj.msgs[i].text + "<br>");
            }
        }
    }

    $("#archive_day_private").click(function(){
        var id = $("#to").val();
        if(id && id!=myID){
            var msgdata = {'opcode':'getRoom', 'from':myID, 'to':id};
            var args = {type:"POST", url:"/chat/chat_m/", data:msgdata, complete:getRoom};
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
                var args = {type:"POST", url:"/chat/archive_messages/", data:msgdata, complete:printArchive_private};
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
                $("#private_area").append(obj.msgs[i].text + "<br>");
            }
        }
    }

});
