/* get id and name of a specific user. */
var selectID = null;
var UserName = null;

/* Private chat staff */
var firstFreeChat = 1;
var max_room = 1;
var max_boxes = 2;
var private_users = [];
private_users[0] = new Private('global', 0, "", null);

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

function my_add(x , y){
    return (x + y);
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
}

Private.prototype.getInfo = function(){
    return "Room: " + this.room_id + "</br>User: " + this.user_name + "</br>Log_numer: " + this.log_number;
};

function switch_chat_box(id, with_id) {
    var aux = private_users[id];
    private_users[id] = private_users[with_id];
    private_users[with_id] = aux;
    $("#PrivateboxTextArea" + with_id).html(private_users[with_id].text_context);
    put_box_name(with_id, private_users[with_id].user_name);
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
    }
    else {
        $('#Privatebar' + room).attr('style', "background: red");
        $('#PrivatebarMinimize' + room).attr('style', "background: red");
    }
}

/* blinking staff. */
function stop_timer_for_swiching(id) {
    clearTimeout(private_users[id].time_set);
    $('#Privatebar' + id).attr('style', "background: blue");
    $('#PrivatebarMinimize' + id).attr('style', "background: blue");
    private_users[id].timer = null;
}

$(document).ready(function () {

    /* csrf crap */
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
        if (firstFreeChat <= max_boxes + 1) {
            for (i = from; i < firstFreeChat - 1; i++) {
                //text_context[i+1]  = $("#PrivateboxTextArea" + (i + 1)).html();
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
    }

    /* Sending private messages */
    var SendMessage = function (id) {
        var name;
        if(id == 0) name = '#GlobalboxTextBox';
        else name = '#PrivateboxTextBox' + id;
        var input = $(name).val();
        if (input) {
            AddToHist(input);
            var msgdata = {'opcode':'message', 'msg':input, 'room':private_users[id].room_id};
            var args = {type:"POST", url:"m/", data:msgdata, complete:ReceiveMessage};
            $.ajax(args);
            $(name).val("");
        }
        return false;
    };

    /* Give old log to the players when they ask. */
    function give_me_old_log(id) {
        var msgdata = {'room':private_users[id].room_id, 'number':private_users[id].log_number};
        var args = {type:"POST", url:"privateLog/", data:msgdata, complete:PrintOnTextArea};
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
    };

    /* Generate private boxes when you need.*/
    function init_chat(id) {
        //Position in page
        var position = 175 * id;
        var html = '<div class="Privatebox" id="Privatebox' + id + '" style="right: ' + position + 'px">' +
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
            '<div class="Privatebox" id="PrivateboxMinimize' + id + '" style="right: ' + position + 'px">' +
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
        });

        $("#UserNameMinimize" + id).click(function () {
            stop_timer_for_swiching(id);
            $("#Privatebox" + id).show();
            $("#PrivateboxMinimize" + id).hide();
        });

        $("#PrivateboxTextBox" + id).click(function () {
            stop_timer_for_swiching(id);
        });

        $("#PrivateboxTextArea" + id).click(function () {
            stop_timer_for_swiching(id);
        });

        $("#PrivateboxTextBox" + id).keyup(function (event) {
            stop_timer_for_swiching(id);
            if (event.keyCode == 13) {
                SendMessage(id);
            }
        });

        $("#OldLog" + id).click(function () {
            give_me_old_log(id);
            stop_timer_for_swiching(id);
        });

        $("#PrivateboxMinimize" + id).hide();
        max_room++;
    }

    /* clear on refresh */
    $('#GlobalboxTextBox').val('');

    /* profile button */
    $("#GlobalboxProfileButton").click(function () {
        window.location = "/player/" + selectID + "/";
    });

    /* write a messaje button */
    $("#GlobalboxMesajeButton").click(function () {
        window.location = "/m/create/to=" + selectID;
    });

    $("#GlobalboxSpellButton").click(function (){
        window.location = "/player/cast/to-" + selectID;
    });

    $("#GlobalboxChallengeButton").click(function (){
        window.location = "/g/challenge/launch/" + selectID;
    });

    var sw = 0;
    function select_bar(id, name) {
        if (sw == 0) {
            var position = 175 * (max_boxes + 1);
            html = '<select onchange="on_selectbar_change()" class= "Privatebox" id="selectbar_id" style="right: ' + position + 'px; background: green;">' +
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
        var msgdata = {'opcode':'getRoom', 'from':myID, 'to':sendID};
        var args = {type:"POST", url:"m/", data:msgdata, complete:create_chat_box};
        $.ajax(args);
        $("#Contactbox").hide();
    });

    /* Create chat box and place it on screen */
    function create_chat_box(res) {
        var obj = jQuery.parseJSON(res.responseText);
        var setName;
        chat_room = obj.name;

        /* Put the name on the list, if windows number is passed.*/
        room = GetRoom(chat_room);
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
                if (max_room > firstFreeChat)
                    $('#Privatebox' + firstFreeChat).show();
                else
                    init_chat(firstFreeChat);
                put_box_name(firstFreeChat, setName);
            }
            /*Initialize values.*/
            private_users[firstFreeChat] = new Private(chat_room, 0, '', setName);
            firstFreeChat++;
        }
    }

    /* Scrolling down function */
    function AutoScroll() {
        $('#GlobalboxTextArea').scrollTop($('#GlobalboxTextArea')[0].scrollHeight);
    }

    /* Update users list */
    function NewUsers() {
        $.get('/chat/last/', function (data) {
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
        $.get('/chat/log/', function (data) {
            $('#GlobalboxTextArea').html(replace_emoticons(data));
            $(document).ready(AutoScroll);
        });
    }

    /* See if I got new message */
    function SendPing() {
        var mdata = {'opcode':'keepAlive'};
        var args = {type:'POST', url:'m/', data:mdata, complete:ReceiveMessage};
        $.ajax(args);
        initial = 0;
    }

    $(document).ready(AutoScroll);
    $(document).ready(NewUsers);
    $(document).ready(NewLog);
    $(document).ready(SendPing);
    $(document).everyTime(6000, NewUsers);
    $(document).everyTime(1000, SendPing);

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
            for (i = 0; i < obj.count; ++i) {
                if (obj.msgs[i].room == 'global' && initial == 0) {
                    $('#GlobalboxTextArea').append(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />");
                    AutoScroll();
                }
                else {
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
                }
            }
        }
        /*For not spaming*/
        else if (res.status == 400) {
            $('#GlobalboxTextArea').append('<p id="warn_spam"> Stop spamming! </p>');
        }
        else if (res.status == 500) {
            alert(res.textContent);
        }
    };

    /* create an emtpy array sized for 10 elements */
    var hist = [];
    var i = hist.length % 10; // iter pentru inserare
    var j = (i + 9) % 10; // iter pentru de unde incepe cautarea
    var k = 0; // iter pentru pasi de history
    var nr_max_steps; // limita pt k
    var change_dir; // anti inertie la schimbare de directie
    var was_writing;
    var initial = 1;

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
            //j = (j + 1) % 10;
            /*k--;*/
        }
        if (k) {
            j = (j + 1) % 10;
            $('#GlobalboxTextBox').val(hist[j]);
            k--;
        }
    }

    $('#GlobalboxSendButton').click(function(){
        SendMessage(0);
    });

    /* Global chat key events. */
    $("#GlobalboxTextBox").keyup(function (event) {
        if (event.keyCode == 13) {
            /* enter */
            $("#GlobalboxSendButton").click();
        }
        else if (event.keyCode == 38) {
            /* up_arrow */
            HistUp();
        }
        else if (event.keyCode == 40) {
            /* down_arrow */
            HistDown();
        }
        else {
            /* other key */
            was_writing = 1;
        }
    });

    /* Emoticons and the replace function. */
    /* TODO: More emoticons.*/
    var emoticons = {
        '>:D':'emoticon_evilgrin.png',
        ':D':'emoticon_grin.png',
        '=D':'emoticon_happy.png',
        ':\\)':'emoticon_smile.png',
        ':O':'emoticon_surprised.png',
        ':P':'emoticon_tongue.png',
        ':\\(':'emoticon_unhappy.png',
        ':3':'emoticon_waii.png',
        ';\\)':'emoticon_wink.png',
        '\\(ball\\)':'sport_soccer.png'
    };

    var img_dir = "/static/img/";
    function replace_emoticons(text) {
        $.each(emoticons, function (character, img) {
            var re = new RegExp(character, 'g');
            text = text.replace(re, '<img src="' + img_dir + img + '" />');
        });
        return text;
    }


    $("#ContactboxProfileButton").click(function(){
        $("#GlobalboxProfileButton").click();
    });

    $("#ContactboxMesajeButton").click(function(){
        $("#GlobalboxMesajeButton").click();
    });

    $("#ContactboxChatButton").click(function(){
        $("#GlobalboxChatButton").click();
    });
});
