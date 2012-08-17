
function send_message(callback){
    var data_msg = {'opcode':'message', 'msg':'salut', 'room':'global'};

    $.ajax(
        {
            type:"POST",
            url:"/chat/chat_m/",
            data: data_msg,
            complete:callback
        }
    )
}

test("send_message", function(){
    stop();
    send_message(
        function(response, status){
            equal(status, "succces");
            var obj = $.parseJSON(response.responseText);
            if(!obj)
                ok(true, "exista");

            start();
        });

});
