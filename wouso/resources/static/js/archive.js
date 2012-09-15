
$(function() {
    $('#datepicker').datepicker();
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
            msgdata = {'date':date};
            var args = {type:"POST", url:"/chat/archive_messages/", data:msgdata, complete:printArchive};
            $.ajax(args);
        }
        else{
            alert($("#slider").slider("values"))

        }

    });


    function printArchive(res, status){
        if(status == "success"){
            $("#ArchiveTextArea").html("");
            var obj = jQuery.parseJSON(res.responseText);
            var i;
            for(i = 0; i < obj.count; i++){
                $("#ArchiveTextArea").append(obj.msgs[i].text + "<br>");
            }
        }

    }
});
