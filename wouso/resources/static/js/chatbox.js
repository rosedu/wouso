/* get id and name of a specific user. */
var selectID = null;
var UserName = null;
var NewUserTimer = null;
var SendPingTimer = null;
var TimeOut = null;
var title;
var timeStamp = null;
var keepAlive = null;
var oneMinute = 60000;

var url_base = '';

/* Private chat staff */
var firstFreeChat;
var max_room;
var max_boxes;
var private_users;

$(function(){
    var socket;
    var name, started = false;

    var connected = function() {
        socket.subscribe("global" + 1);
        socket.send({room:'global', action: 'start'});

    };

    $('#GlobalboxSendButton').click(function() {
        var value = $('#GlobalboxTextBox').val();
        if (value) {
            var data = {'action':'message', 'msg':value, 'room':'global'};
            socket.send(data);
        }
        $('#GlobalboxTextBox').val('').focus();
        return false;
    });

    function addMessage(data){

        $("#GlobalboxTextArea").append("<em>" +data.name + " ***: " + replace_emoticons(data.msg) + "</em><br />");
        //$('#GlobalboxTextArea').append("<em>" + obj.msgs[i].time + " ***: " + replace_emoticons(obj.msgs[i].text) + "</em><br />");

    }
    /*
    var addMessage = function(data) {
        var d = new Date();
        var win = $(window), doc = $(window.document);
        var bottom = win.scrollTop() + win.height() == doc.height();
        data.time = $.map([d.getHours(), d.getMinutes(), d.getSeconds()],
            function(s) {
                s = String(s);
                return (s.length == 1 ? '0' : '') + s;
            }).join(':');
        addItem('#messages', data);
        if (bottom) {
            window.scrollBy(0, 10000);
        }
    };
    */

    var messaged = function(data) {
        switch (data.action) {

            case 'message':
                addMessage(data);
                break;
        }
    };

    var start = function() {
        socket = new io.Socket();
        socket.connect();

        socket.on('connect', connected);
        socket.on('message', messaged);

    };


    start();
});
if(sessionStorage.firstFreeChat){
    firstFreeChat = parseInt(sessionStorage.firstFreeChat);
    max_room = 1;
    max_boxes = parseInt(sessionStorage.max_boxes);
    private_users = JSON.parse(sessionStorage.private_users);
    keepAlive = parseInt(sessionStorage.keepAlive);
}
else{
    firstFreeChat = 1;
    max_room = 1;
    max_boxes = 5;
    private_users = [];
    private_users[0] = new Private('global', 0, "", null);
    keepAlive = 1000;
    sessionStorage.keepAlive = keepAlive;
    sessionStorage.firstFreeChat = firstFreeChat;
    sessionStorage.max_room = max_room;
    sessionStorage.max_boxes = max_boxes;
    sessionStorage.private_users = JSON.stringify(private_users);
}

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

var img_dir = "/static/img/"; // TODO: fixme, use base_url
function replace_emoticons(text) {
    $.each(emoticons, function (character, img) {
        var re = new RegExp(character, 'g');
        text = text.replace(re, '<img src="' + img_dir + img + '" />');
    });
    return text;
}

function put_box_name(id, user) {
    $("#UserName" + id).attr('value', user);
    $("#UserNameMinimize" + id).attr('value', user);
}

function get_selected_value() {
    var value = $("#selectbar_id option:last").val();
    if (firstFreeChat == (max_boxes + 1))
        $("#selectbar_id").hide();
    return value;
}

function remove_last() {
    $("#selectbar_id option:last").remove();
}

function Private(room_id, log_number, text_context, users_name){
    this.room_id =room_id;
    this.log_number = log_number;
    this.text_context = text_context;
    this.user_name = users_name;
    this.timer = null;
    this.time_set = null;
    this.hidden_position = true;
}

function switch_chat_box(id, with_id) {
    var aux = private_users[id];
    private_users[id] = private_users[with_id];
    private_users[with_id] = aux;
    $("#PrivateboxTextArea" + with_id).html(private_users[with_id].text_context);
    put_box_name(with_id, private_users[with_id].user_name);
    sessionStorage.private_users = JSON.stringify(private_users);
}



function on_userlist_select(id, Name) {
    selectID = id;
    UserName = Name;

    $('.cl_item').attr('style', 'font-weight: normal');
    $('#cl_' + id).attr('style', 'font-weight: bold; background-color:#ffffff;');
    $('.caction').attr('disabled', false);
    if (selectID == myID){
        $('#GlobalboxChatButton').attr('disabled', true);
        $('#GlobalboxChallengeButton').attr('disabled', true);
    }
}

function on_selectbar_change() {
    var id = $("#selectbar_id option:selected").val();
    switch_chat_box(id, 1);
    $("#selectbar_id").append('<option value="' + id + '" >' +  private_users[id].user_name + '  </option>');

    $("#selectbar_id option:selected").remove();
    $("#selectbar_id option:first").attr('selected', 'selected');
}

/* Blink box header, when receive a new message */
function switch_color(room) {
    if (private_users[room].timer++ % 2 == 0) {
        $('#Privatebar' + room).attr('style', "background: blue");
        $('#PrivatebarMinimize' + room).attr('style', "background: blue");
        document.title = title;
    }
    else {
        $('#Privatebar' + room).attr('style', "background: red");
        $('#PrivatebarMinimize' + room).attr('style', "background: red");
        document.title = private_users[room].user_name+ " spune...";
    }
}

/* blinking staff. */
function stop_timer_for_swiching(id) {
    clearTimeout(private_users[id].time_set);
    $('#Privatebar' + id).attr('style', "background: blue");
    $('#PrivatebarMinimize' + id).attr('style', "background: blue");
    private_users[id].timer = null;
    private_users[id].time_set = null;
    sessionStorage.private_users = JSON.stringify(private_users);
    document.title = title;
}

$(document).ready(function () {
    title = document.title;
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

    function change_values(from, to){
        $("#PrivateboxTextArea" + to).html(private_users[from].text_context);
        private_users[to] = private_users[from];
    }

    /* Switching on close */
    function switch_windows(from) {
        var i;
        var max_value = max_room + 1;
        if (firstFreeChat <  max_value) {
            for (i = from; i < firstFreeChat - 1; i++) {
                stop_timer_for_swiching(i);
                change_values(i + 1, i);
                put_box_name(i, private_users[i].user_name);

                /* Put the same status as before. */
                if ($("#Privatebox" + (i + 1)).is(":visible")) {
                    $("#Privatebox" + i).show();
                    $("#PrivateboxMinimize" + i).hide();
                } else {
                    $("#Privatebox" + i).hide();
                    $("#PrivateboxMinimize" + i).show();
                }

            }

            firstFreeChat--;
            /* Hide and remove old info. */
            stop_timer_for_swiching(firstFreeChat);
            $("#PrivateboxTextArea" + firstFreeChat).text("");
            $("#Privatebox" + firstFreeChat).hide();
            $("#PrivateboxMinimize" + firstFreeChat).hide();
        } else {
            firstFreeChat--;
            var last = get_selected_value();
            change_values(last, from);
            put_box_name(from, private_users[from].user_name);
            remove_last();
        }
        sessionStorage.private_users = JSON.stringify(private_users);
        sessionStorage.firstFreeChat = firstFreeChat;
    }

    /* Sending private messages */
    var SendMessage = function (id) {
        var name;
        if(id == 0) name = '#GlobalboxTextBox';
        else name = '#PrivateboxTextBox' + id;
        var input = $(name).val();
        if (input) {
            AddToHist(input);
            var msgdata = {'opcode':'message', 'msg':input, 'room':private_users[id].room_id, 'time': timeStamp};
            var args = {type:"POST", url:url_base + "/chat/chat_m/", data:msgdata, complete:ReceiveMessage};
            $.ajax(args);
            $(name).val("");
        }
        return false;
    };

    /* Give old log to the players when they ask. */
    function give_me_old_log(id) {
        var msgdata = {'room':private_users[id].room_id, 'number':private_users[id].log_number};
        var args = {type:"POST", url:url_base + "/chat/privateLog/", data:msgdata, complete:PrintOnTextArea};
        $.ajax(args);
        return false;
    }

    var PrintOnTextArea = function (res) {
        var obj = jQuery.parseJSON(res.responseText);
        if (!obj) {
            return false;
        }
        var i, room = GetRoom(obj.msgs[1].room);
        private_users[room].log_number += obj.count;
        for (i = obj.count - 1; i >= 0; --i) {
            var log_text = obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />";
            private_users[room].text_context = log_text + private_users[room].text_context;
            $('#PrivateboxTextArea' + room).prepend(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />");
        }
        sessionStorage.private_users = JSON.stringify(private_users);
    };

    /* Generate private boxes when you need.*/
    function init_chat(id) {
        //Position in page
        var position = 175 * id;
        var html = '<div class="Privatebox" id="Privatebox' + id + '" style="right: ' + position + 'px; position:fixed">' +
            '    <div id="Privatebar' + id + '" style="background: blue">' +
            '        <input type="button" id="UserName' + id + '" class="PrivateboxUserName"/>' +
            '        <input type="button" id="ExitButton' + id + '" class="PrivateboxExitButton" value="x"/>' +
            '    </div>' +
            '    <div>' +
            '       <a href="#" style="padding: 3px" id="OldLog' + id + '"> show older log...</a>' +
            '       <div id="PrivateboxTextArea' + id + '" class="PrivateboxTextArea" ></div>' +
            '    </div>' +
            '    <input type="text" id="PrivateboxTextBox' + id + '" class="PrivateboxTextBox"/>' +
            '</div>' +
            '<div class="Privatebox" id="PrivateboxMinimize' + id + '" style="right: ' + position + 'px; ; position:fixed">' +
            '    <div id="PrivatebarMinimize' + id + '" style="background: blue">' +
            '      <input type="button" id="UserNameMinimize' + id + '"   class="PrivateboxUserName"/>' +
            '      <input type="button" id="ExitButtonMinimize' + id + '" class="PrivateboxExitButton" value="x"/>' +
            '    </div>' +
            '</div>';

        $("#PrivateChatBoxes").append(html);

        $("#ExitButton" + id).click(function () {
            switch_windows(id);
            stop_timer_for_swiching(id);
        });

        $("#ExitButtonMinimize" + id).click(function () {
            switch_windows(id);
            stop_timer_for_swiching(id);
        });

        $("#UserName" + id).click(function () {
            stop_timer_for_swiching(id);
            $("#Privatebox" + id).hide();
            $("#PrivateboxMinimize" + id).show();
            private_users[id].hidden_position = false;
            sessionStorage.private_users = JSON.stringify(private_users);
        });

        $("#UserNameMinimize" + id).click(function () {
            stop_timer_for_swiching(id);
            $("#Privatebox" + id).show();
            $("#PrivateboxMinimize" + id).hide();
            private_users[id].hidden_position = true;
            sessionStorage.private_users = JSON.stringify(private_users);
        });

        $("#PrivateboxTextBox" + id).click(function () {
            stop_timer_for_swiching(id);
        });

        $("#PrivateboxTextArea" + id).click(function () {
            stop_timer_for_swiching(id);
            $("#PrivateboxTextBox" + id).focus();
        });

        $("#PrivateboxTextBox" + id).keydown(function (event) {
            stop_timer_for_swiching(id);
            if (event.keyCode == 13) {
                SendMessage(id);
            }
            if (event.keyCode == 27){
                switch_windows(id);
            }
            if (event.keyCode == 9){
                var next;
                if(firstFreeChat > max_boxes)
                    next = id % max_boxes + 1;
                else{
                    next = (id + 1) % firstFreeChat;
                    if(next == 0) next = 1
                }
                $("#PrivateboxTextBox" + next).focus();
                return false;
            }

        });

        $("#OldLog" + id).click(function () {
            give_me_old_log(id);
            stop_timer_for_swiching(id);
        });

        $("#PrivateboxMinimize" + id).hide();
        max_room++;
        sessionStorage.max_room = max_room;
    }

    /* clear on refresh */
    $('#GlobalboxTextBox').val('');

    /* profile button */
    $("#GlobalboxProfileButton").click(function () {
        window.location = url_base + "/player/" + selectID + "/";
    });

    /* write a messaje button */
    $("#GlobalboxMesajeButton").click(function () {
        window.location = url_base + "/m/create/to=" + selectID;
    });

    $("#GlobalboxSpellButton").click(function (){
        window.location = url_base + "/player/cast/to-" + selectID;
    });

    $("#GlobalboxChallengeButton").click(function (){
        window.location = url_base + "/g/challenge/launch/" + selectID;
    });

    var sw = 0;
    function select_bar(id, name) {
        if (sw == 0) {
            var position = 175 * (max_boxes + 1);
            html = '<select onchange="on_selectbar_change()" class= "Privatebox" id="selectbar_id" style="right: ' + position + 'px; background: green; position:fixed">' +
                '<option ></option>' +
                '</select>';
            $("#PrivatebarUsers").append(html);
            sw = 1;
            $("#selectbar_id").show();
        }
        if ($("#selectbar_id").is(":hidden"))
            $("#selectbar_id").show();
        $("#selectbar_id").append('<option value="' + id + '" >' + name + '  </option>');
    }

    $("#GlobalboxChatButton").click(function () {
        var sendID = (selectID_over != null)? selectID_over: selectID;
        var msgdata = {'opcode':'getRoom', 'from':myID, 'to':sendID, 'time': timeStamp};
        var args = {type:"POST", url:url_base + "/chat/chat_m/", data:msgdata, complete:create_chat_box};
        $.ajax(args);
        $("#Contactbox").hide();
    });

    /* Create chat box and place it on screen */
    function create_chat_box(res) {
        var obj = $.parseJSON(res.responseText);
        var setName;
        var chat_room = obj.name;
        /* Put the name on the list, if windows number is passed.*/
        var room = GetRoom(chat_room);
        if (UserName_over != null){
            setName = UserName_over;
            selectID_over = null;
            UserName_over = null;
        }
        else setName = UserName;
        if (room == firstFreeChat){
            if(firstFreeChat > max_boxes) {
                /* Create and put in the select_bar */
                select_bar(firstFreeChat, setName);
            }
            /* Create or show next box.*/
            else{
                if (max_room > firstFreeChat){
                    $('#Privatebox' + firstFreeChat).show();

                }else
                    init_chat(firstFreeChat);
                put_box_name(firstFreeChat, setName);
                $("#PrivateboxTextBox" + firstFreeChat).focus();
            }
            /*Initialize values.*/
            private_users[firstFreeChat] = new Private(chat_room, 0, '', setName);
            firstFreeChat++;
        }
        sessionStorage.private_users = JSON.stringify(private_users);
        sessionStorage.firstFreeChat = firstFreeChat;
    }

    /* Scrolling down function */
    function AutoScroll() {
        $('#GlobalboxTextArea').scrollTop($('#GlobalboxTextArea')[0].scrollHeight);
    }

    /* Update users list */
    function NewUsers() {
        $.get(url_base + '/chat/last/', function (data) {
            $('#GlobalboxUserList').html(data);
            if (selectID) {
                $('#cl_' + selectID).attr('style', 'font-weight: bold;background-color:#ffffff;');
                $('.caction').attr('disabled', false);
                if (selectID == myID){
                    $('#GlobalboxChatButton').attr('disabled', true);
                    $('#GlobalboxChallengeButton').attr('disabled', true);
                }

            }
            else
                $('.caction').attr('disabled', true);
        });
    }

    /* Last 50 messages that was write in global chat.*/
    function NewLog() {
        $.get(url_base + '/chat/log/', function (data) {
            $('#GlobalboxTextArea').html(replace_emoticons(data));
            $(document).ready(AutoScroll);
        });
    }

    /* See if I got new message */
    function SendPing() {

        var mdata = {'opcode':'keepAlive', 'time': timeStamp};
        var args = {type:'POST', url:url_base + '/chat/chat_m/', data:mdata, complete:ReceiveMessage};
        $.ajax(args);
    }

    function InitialChat(){
        var i;
        for(i = 1; i <  firstFreeChat; i++){
            if(i > max_boxes) {
                /* Create and put in the select_bar */
                select_bar(i, private_users[i].user_name);
            }
            /* Create or show next box.*/
            else{
                init_chat(i);
                put_box_name(i, private_users[i].user_name);
                $("#PrivateboxTextArea" + i).html(private_users[i].text_context);
                if(private_users[i].time_set)
                    private_users[i].time_set = setInterval('switch_color(' + i + ')', 500);
                if(private_users[i].hidden_position == false){
                        $("#Privatebox" + i).hide();
                        $("#PrivateboxMinimize" + i).show();
                }
            }
        }
    }


    $(document).ready(AutoScroll);
    $(document).ready(NewUsers);
    $(document).ready(NewLog);
    //$(document).ready(SendPing);
    //SendPingTimer = setInterval(function(){SendPing();}, keepAlive);
    NewUserTimer = setInterval(function(){NewUsers();}, 10000);
    InitialChat();

    function SetTimeForKeepAlive(time){
        clearInterval(SendPingTimer);
        keepAlive = time;
        sessionStorage.keepAlive = keepAlive;
        SendPingTimer = setInterval(function(){SendPing();}, keepAlive);

    }

    TimeOut = setTimeout(function(){SetTimeForKeepAlive(5000)}, oneMinute);

    /* Give room id or next free chat.*/
    function GetRoom(room) {
        for (var i = 1; i < firstFreeChat; i++)
            if (private_users[i].room_id == room)
                return i;
        return firstFreeChat
    }

    /* Receive function for every kind of messages.*/
    var ReceiveMessage = function (res, status) {
        if (status == "success") {
            var obj = jQuery.parseJSON(res.responseText);
            if (!obj)
                return false;
            var i;
            timeStamp = obj.time;
            for (i = 0; i < obj.count; ++i) {
                if(obj.msgs[i].mess_type == 'special' && obj.msgs[i].comand == 'block-communication'){
                    clearInterval(NewUserTimer);
                    clearInterval(SendPingTimer);
                    if(window.location.pathname == url_base + "/chat/")
                        window.location = url_base + "/"
                }
                else if(obj.msgs[i].mess_type == 'special' && obj.msgs[i].comand == 'kick' && window.location.pathname == url_base + '/chat/'){
                    window.location = url_base + "/";
                }
                else if(obj.msgs[i].user == myName && obj.msgs[i].mess_type == 'special')
                    continue;
                else if (obj.msgs[i].mess_type == 'activity') {
                    $('#GlobalboxTextArea').append("<em>" + obj.msgs[i].time + " ***: " + replace_emoticons(obj.msgs[i].text) + "</em><br />");
                    AutoScroll();
                }
                else if (obj.msgs[i].room == 'global') {
                    $('#GlobalboxTextArea').append(obj.msgs[i].time + obj.msgs[i].user + ": " + replace_emoticons(obj.msgs[i].text) + "<br />");
                    AutoScroll();
                    if(window.location.pathname == url_base + '/chat/'){
                        clearTimeout(TimeOut);
                        SetTimeForKeepAlive(1000);
                        TimeOut = setTimeout(function(){SetTimeForKeepAlive(5000)}, oneMinute);
                    }
                }
                else {
                    clearTimeout(TimeOut);
                    SetTimeForKeepAlive(1000);
                    TimeOut = setTimeout(function(){SetTimeForKeepAlive(5000)}, oneMinute);
                    var room = GetRoom(obj.msgs[i].room);
                    if(room == firstFreeChat){
                        firstFreeChat++;
                        if (room > max_boxes) {
                            select_bar(room, obj.msgs[i].user);
                        }
                        else {
                            if (max_room > room)
                                $('#Privatebox' + room).show();
                            else
                                init_chat(room);
                            put_box_name(room, obj.msgs[i].user);
                        }
                        private_users[room] = new Private(obj.msgs[i].room, 0, '', obj.msgs[i].user);
                        $("#Privatebox" + room).show();
                    }
                    private_users[room].log_number ++;
                    private_users[room].text_context +=obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + " <br />";

                    if (room <= max_boxes){
                        if (obj.msgs[i].user != myName && private_users[room].timer == null) {
                            private_users[room].timer = 1;
                            private_users[room].time_set = setInterval('switch_color('+room+')', 500);
                        }
                        $('#PrivateboxTextArea' + room).append(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />");
                        $('#PrivateboxTextArea' + room).scrollTop($('#PrivateboxTextArea' + room)[0].scrollHeight);
                    }
                    sessionStorage.private_users = JSON.stringify(private_users);
                    sessionStorage.firstFreeChat = firstFreeChat;
                }
            }
        }
        /*For not spaming*/
        else if (res.status == 400) {
            $('#GlobalboxTextArea').append('<p id="warn_spam"> Stop spamming! </p>');
        }
    };

    //TODO:hist things
    /* create an emtpy array sized for 10 elements */
    var hist = [];
    var i = hist.length % 10; // iter pentru inserare
    var j = (i + 9) % 10; // iter pentru de unde incepe cautarea
    var k = 0; // iter pentru pasi de history
    var nr_max_steps; // limita pt k
    var change_dir; // anti inertie la schimbare de directie
    var was_writing;

    function AddToHist(input) {
        /* adds input to history array */
        hist[i] = input;
        i = (i + 1) % 10;
        j = (i + 9) % 10;
        nr_max_steps = hist.length;
        k = 0;
        was_writing = 0;
    }

    /* History for keys.*/
    function HistUp() {
        if (was_writing) {
            /* bagat in hist */
            var input = $('#GlobalboxTextBox').val();
            if (input) {
                hist[i] = input;
                i = (i + 1) % 10;
                j = (i + 8) % 10;
                nr_max_steps = hist.length;
                k++;
                was_writing = 0;
            }
        }
        if (k < nr_max_steps) {
            $('#GlobalboxTextBox').val(hist[j]);
            j = (j + 9) % 10;
            k++;
            change_dir = 1;
        }
    }

    function HistDown() {
        if (k == 0 && !was_writing) {
            $('#GlobalboxTextBox').val("");
        }
        else if (change_dir) {
            change_dir = 0;
        }
        if (k) {
            j = (j + 1) % 10;
            $('#GlobalboxTextBox').val(hist[j]);
            k--;
        }
    }

    //$('#GlobalboxSendButton').click(function(){
    //    SendMessage(0);
    //});

    /* Global chat key events. */
    $("#GlobalboxTextBox").keyup(function (event) {
        if (event.keyCode == 13) {
            $("#GlobalboxSendButton").click();
        }
        else if (event.keyCode == 38) {
            HistUp();
        }
        else if (event.keyCode == 40) {
            HistDown();
        }
        else {
            was_writing = 1;
        }
    });
});