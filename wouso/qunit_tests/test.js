
function send_message(data_msg, callback){
    $.ajax(
        {
            type:"POST",
            url:"/chat/chat_m/",
            data: data_msg,
            complete:callback
        }
    )
}

test("Send message on global chat from connected user.", function(){
    stop();
    var data_msg = {'opcode':'message', 'msg':'salut', 'room':'global'};
    send_message(
        data_msg,
        function(response, status){
            equal(status, "success");
            var obj = $.parseJSON(response.responseText);
            if(!obj)
                ok(true, "exista");
            equal(obj.count, 1, "Message number");
            equal(obj.msgs[0].user,"iulian","user");
            equal(obj.msgs[0].text,"salut","message");
            start();
        });
});
var chat_room = null;

test("Create or get room ajax test.", function(){
    stop();
    var msgdata = {'opcode':'getRoom', 'from':1, 'to':2};
    send_message(
        msgdata,
        function(response, status){
            equal(status, "success");
            var obj = $.parseJSON(response.responseText);
            chat_room = obj.name;
            if(!obj)
                ok(true, "exista");
            equal(chat_room,"1-2","room_name");
            start();

        });

});

test("Message in a room", function(){
    equal(chat_room,"1-2","again room_name");
    stop();
    var data_msg = {'opcode':'message', 'msg':'salut', 'room':chat_room};
    send_message(
        data_msg,
        function(response, status){
            equal(status, "success");
            var obj = $.parseJSON(response.responseText);
            if(!obj)
                ok(true, "exista");
            equal(obj.count, 1, "Message number");
            equal(obj.msgs[0].user,"iulian","user");
            equal(obj.msgs[0].text,"salut","message");
            start();
        });


});