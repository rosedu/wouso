
$(function() {
    $( "#datepicker" ).datepicker();
});

$(document).ready(function(){

    $("#archive_day").click(function(){
        var date = $("#datepicker").val();
        if(date){
            msgdata = {'date':date};
            var args = {type:"POST", url:"/chat/archive_messages/", data:msgdata, complete:printArchive};
            $.ajax(args);
        }
        else
            alert("Nu a fost selectat nimic")
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
