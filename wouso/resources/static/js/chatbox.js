/* get id and name of a specific user. */
var selectID = null;
var UserName = null;


/* Private chat staff */
var firstFreeChat = 1;
var room_id = [];
var max_room = 1;
var chat_room = "null=null";
var log_number = [];
var text_context = [];
var users_name = [];

function PutBoxName(id) {
    $("#UserName" + id).attr('value', users_name[id]);
    $("#UserNameMinimize" + id).attr('value', users_name[id]);
}

/* TODO: change name.*/
function getval() {

    var value = $("#zz option:last").val();
    if (firstFreeChat == 3)
        $("#zz").hide();
    return value;
}

/* TODO: Change zz name*/
function remove_last() {
    $("#zz option:last").remove();

}

/* TODO: Change name.*/
function SW(id, with_id) {

    var aux = log_number[id];
    log_number[id] = log_number[with_id];
    log_number[with_id] = aux;

    if (text_context[id] == "") {
        $("#OldLog" + with_id).remove();
        text_context[id] = $("#PrivateboxTextArea1").html();
        $("#PrivateboxTextArea" + with_id).text("");
        //$("#PrivateboxTextArea" + switch_box).prepend('<a href="#"  id="OldLog' + switch_box + '"> show older log...</br> </a>');
    }
    else {
        aux = text_context[id];
        text_context[id] = $("#PrivateboxTextArea" + with_id).html();
        $("#PrivateboxTextArea1").html(aux);
        //$("#PrivateboxTextArea" + switch_box).prepend('<a href="#"  id="OldLog' + switch_box + '"> show older log...</br> </a>');
    }

    aux = users_name[id];
    users_name[id] = users_name[with_id];
    users_name[with_id] = aux;

    aux = room_id[id];
    room_id[id] = room_id[with_id];
    room_id[with_id] = aux;

    PutBoxName(with_id);
}


function select(id, Name) {
    selectID = id;
    UserName = Name;

    $('.cl_item').attr('style', 'font-weight: normal');
    $('#cl_' + id).attr('style', 'font-weight: bold; background-color:#ffffff;');
    $('.caction').attr('disabled', false);
}

/* TODO: changre*/
var aa = function () {
    //$("#zz").attr("tabindex", 1);
    $("#ShoutboxUserList").append("mata");
    id = $("#zz option:selected").val();
    SW(id, 1);
    $("#zz").append('<option value="' + id + '" >' + users_name[id] + '  </option>');

    $("#zz option:selected").remove();
    $("#zz option:first").attr('selected', 'selected');
};

/* blink box header when receive a new message */
var timer = [];
function SwitchColor(room) {

    if (timer[room] % 2 == 0) {
        $('#Privatebar' + room).attr('style', "background: blue");
        $('#PrivatebarMinimize' + room).attr('style', "background: blue");
    }
    else {
        $('#Privatebar' + room).attr('style', "background: red");
        $('#PrivatebarMinimize' + room).attr('style', "background: red");
    }
    timer[room]++;
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


    /* blinking staff. */
    var ti = [];
    var StopTimer = function (id) {
        clearTimeout(ti[id]);
        $('#Privatebar' + id).attr('style', "background: blue");
        $('#PrivatebarMinimize' + id).attr('style', "background: blue");
        timer[id] = null;
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


    /* Switching on close */
    /*TODO: get windows status */
    function SwitchWindows(from) {
        var i;
        if (firstFreeChat <= 3) {

            for (i = from; i < firstFreeChat; i++)
                $("#OldLog" + i).remove();

            for (i = from; i < firstFreeChat; i++) {

                /* Switch the text from the right windows. */
                $("#PrivateboxTextArea" + i).html($("#PrivateboxTextArea" + (i + 1)).html());

                /* Insert log button. */
                insert_log_button(i);

                /* Switch the headers.*/
                users_name[i] = users_name[i + 1];
                PutBoxName(i);

                /* Put the same status as before. */
                if ($("#Privatebox" + (i + 1)).is(":visible")) {
                    $("#Privatebox" + i).show();
                    $("#PrivateboxMinimize" + i).hide();
                } else {
                    $("#Privatebox" + i).hide();
                    $("#PrivateboxMinimize" + i).show();
                }

                /* Save the number of messages. */
                log_number [i] = log_number [i + 1];

                /* Save the room_id before switching. */
                room_id[i] = room_id[i + 1];
            }

            firstFreeChat--;

            /* Hide or remove old info. */
            log_number[firstFreeChat] = 0;
            $("#OldLog" + firstFreeChat).remove();
            $("#PrivateboxTextArea" + firstFreeChat).text("");
            $("#Privatebox" + firstFreeChat).hide();
            $("#PrivateboxMinimize" + firstFreeChat).hide();

        } else {
            firstFreeChat--;
            var last = getval();
            $("#PrivateboxTextArea" + from).html(text_context[last]);

            /* Insert log button. */
            insert_log_button(from);

            /* Save the number of messages. */
            log_number [from] = log_number [last];

            users_name[from] = users_name[last];
            PutBoxName(from);

            /* Save the room_id before switching. */
            room_id[from] = room_id[last];
            log_number[last] = 0;

            remove_last();
        }
    }

    /* TODO: Cand apas pe PrivatecboxTextAreea sa ma trimita in field*/

    /* Sending private messages */
    /* TODO: change name!!*/
    var SendMessage1 = function (id) {
        var input = $('#PrivateboxTextBox' + id).val();

        if (input) {
            var msgdata = {'opcode':'message', 'msg':input, 'room':room_id[id]};
            var args = {type:"POST", url:"m/", data:msgdata, complete:ReceiveMessage};
            $.ajax(args);
            $('#PrivateboxTextBox' + id).val("");
        }
        return false;
    };

    /* Give old log to the players when they ask. */
    /* TODO: change url name!!! */
    var GiveMeOldLog = function (id) {

        var msgdata = {'room':room_id[id], 'number':log_number[id]};
        var args = {type:"POST", url:"logP/", data:msgdata, complete:PrintOnTextArea};
        $.ajax(args);
        return false;
    };

    var PrintOnTextArea = function (res) {
        var obj = jQuery.parseJSON(res.responseText);
        if (!obj) {
            return false;
        }

        var i;
        var room = GetRoom(obj.msgs[1].room);
        log_number[room] += obj.count;
        for (i = obj.count - 1; i >= 0; --i) {
            $('#OldLog' + room).after(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />")
        }
        /*TODO: option scroll down.*/
        //$('#PrivateboxTextArea'+room).scrollTop($('#PrivateboxTextArea'+room)[0].scrollHeight);
    };

    function insert_log_button(id) {

        $("#PrivateboxTextArea" + id).prepend('<a href="#"  id="OldLog' + id + '"> show older log...</br> </a>');

        $("#OldLog" + id).click(function () {
            GiveMeOldLog(id);
            StopTimer(id);
        });
    }


    /* Generate private boxes when you need.*/
    function init_chat(id) {
        //Position in page
        var position = 175 * id;
        var html = '<div class="Privatebox" id="Privatebox' + id + '" style="right: ' + position + 'px">' +
            '    <div id="Privatebar' + id + '" style="background: blue">' +
            '        <input type="button" id="UserName' + id + '" class="PrivateboxUserName"/>' +
            '        <input type="button" id="ExitButton' + id + '" class="PrivateboxExitButton" value="x"/>' +
            '    </div>' +
            '    <div id="PrivateboxTextArea' + id + '" class="PrivateboxTextArea" >' +
            //    '        <a href="#"  id="OldLog' + id + '"> show older log...</br> </a>' +

            '    </div>' +
            '    <input type="text" id="PrivateboxTextBox' + id + '" class="PrivateboxTextBox"/>' +
            '</div>' +

            '<div class="Privatebox" id="PrivateboxMinimize' + id + '" style="right: ' + position + 'px">' +
            '    <div id="PrivatebarMinimize' + id + '" style="background: blue">' +
            '      <input type="button" id="UserNameMinimize' + id + '"   class="PrivateboxUserName"/>' +
            '      <input type="button" id="ExitButtonMinimize' + id + '" class="PrivateboxExitButton" value="x"/>' +
            '    </div>' +

            '</div>';

        //Appending
        $("#PrivateChatBoxes").append(html);


        $("#ExitButton" + id).click(function () {
            SwitchWindows(id);
            StopTimer(id);
        });

        $("#ExitButtonMinimize" + id).click(function () {
            SwitchWindows(id);
            StopTimer(id);
        });

        $("#UserName" + id).click(function () {
            StopTimer(id);
            $("#Privatebox" + id).hide();
            $("#PrivateboxMinimize" + id).show();

        });

        $("#UserNameMinimize" + id).click(function () {
            StopTimer(id);
            $("#Privatebox" + id).show();
            $("#PrivateboxMinimize" + id).hide();

        });

        $("#PrivateboxTextBox" + id).click(function () {
            StopTimer(id);
        });

        $("#PrivateboxTextArea" + id).click(function () {
            StopTimer(id);
        });

        $("#PrivateboxTextBox" + id).keyup(function (event) {
            StopTimer(id);
            if (event.keyCode == 13) {
                /* enter */
                SendMessage1(id);
            }
        });

        $("#PrivateboxMinimize" + id).hide();
        log_number[id] = 0;
        max_room++;

    }

    /* clear on refresh */
    $('#ShoutboxTextBox').val('');

    /* hide button */
    $("#ShoutboxHideButton").click(function () {
        $("#Shoutbox").hide("slide", {direction:"right"});
        $("#ShoutboxShowButton").delay("350").show("slide", {direction:"right"});
    });

    /* show button */
    $("#ShoutboxShowButton").click(function () {
        $("#ShoutboxShowButton").hide();
        $("#Shoutbox").show("slide", {direction:"right"});
    });

    /* profile button */
    $("#ShoutboxProfileButton").click(function () {
        if (selectID != null) {
            window.location = "/player/" + selectID + "/";
        }
    });

    /* write a messaje button */
    $("#ShoutboxMesajeButton").click(function () {
        if (selectID != null) {
            window.location = "/m/create/to=" + selectID;
        }
    });


    sw = 0;
    /* TODO: change select ID*/
    function select_bar(id, name) {
        if (sw == 0) {

            html = '<select onchange="aa()" class= "Privatebox" id ="zz" style="right: 1050px; background: green;">' +
                '<option ></option>' +
                '</select>';
            $("#PrivatebarUsers").append(html);
            sw = 1;
            $("#zz").show();
        }
        if ($("#zz").is(":hidden"))
            $("#zz").show();
        $("#zz").append('<option value="' + id + '" >' + name + '  </option>');


    }

    /* chat button*/
    /* TODO: Change name.*/
    $("#C").click(function () {
        if (selectID != null) {

            /* Create chat room name.*/
            if (selectID == myID)
                alert("Nu ai cum sa faci chat cu tine");
            else {
                // Cream camera pe server
                var msgdata = {'opcode':'getRoom', 'from':myID, 'to':selectID};
                var args = {type:"POST", url:"m/", data:msgdata, complete:CreateChatBox};
                $.ajax(args);
            }
        }
    });


    /* Create chat box and place it on screen */
    function CreateChatBox(res, status) {
        var obj = jQuery.parseJSON(res.responseText);

        chat_room = obj.name;

        /* Put the name on the list, if windows number is passed.*/
        if (RoomNotExist(chat_room) && firstFreeChat > 2) {
            /* Create and put in the select_bar */
            select_bar(firstFreeChat, UserName);

            /*Initialize values.*/
            room_id[firstFreeChat] = chat_room;
            users_name[firstFreeChat] = UserName;
            text_context[firstFreeChat] = "";
            log_number[firstFreeChat] = 0;
            firstFreeChat++;

        }
        /* Create or show next box.*/
        else if (RoomNotExist(chat_room)) {
            room_id[firstFreeChat] = chat_room;
            users_name[firstFreeChat] = UserName;
            if (max_room > firstFreeChat)
                $('#Privatebox' + firstFreeChat).show();
            else
                init_chat(firstFreeChat);
            insert_log_button(firstFreeChat);
            $("#UserName" + firstFreeChat).attr('value', users_name[firstFreeChat] + chat_room);
            $("#UserNameMinimize" + firstFreeChat).attr('value', users_name[firstFreeChat]);

            firstFreeChat++;
        }
    }


    /* Scrolling down function */
    function AutoScroll() {
        $('#ShoutboxTextArea').scrollTop($('#ShoutboxTextArea')[0].scrollHeight);
    }

    /* Update users list */
    function NewUsers() {
        $.get('/chat/last/', function (data) {
            $('#ShoutboxUserList').html(data);
            if (selectID) {
                $('#cl_' + selectID).attr('style', 'font-weight: bold;background-color:#ffffff;');
                $('.caction').attr('disabled', false);
            }
            else
                $('.caction').attr('disabled', true);
        });
    }

    /* Last 50 messages that was write in global chat.*/
    /* TODO: Maybe Change the name*/
    function NewLog() {
        $.get('/chat/log/', function (data) {
            $('#ShoutboxTextArea').html(replace_emoticons(data));
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
    $(document).everyTime(6000, NewUsers);
    $(document).everyTime(1000, SendPing);


    function AddToHist(input) {
        /* adds input to history array */
        hist[i] = input;
        i = (i + 1) % 10;
        j = (i + 9) % 10;
        nr_max_steps = hist.length;
        k = 0;
        was_writing = 0;
    }

    function IsForMe(room) {
        var first = room.split("-");
        var i;
        for (i = 0; i < first.length; i++)
            if (myID == first[i])
                return true;

        return false;

    }

    /* Tell me if the room exist.*/
    function RoomNotExist(room) {
        var i;
        for (i = 1; i <= firstFreeChat; i++)
            if (room_id[i] == room)
                return false;
        return true;
    }

    /* Give room id or next free chat.*/
    function GetRoom(room) {
        var i;
        for (i = 1; i <= firstFreeChat; i++)
            if (room_id[i] == room)
                return i;
        firstFreeChat++;
        return firstFreeChat - 1
    }


    /* Send function for global chat.*/
    var SendMessage = function () {
        var input = $('#ShoutboxTextBox').val();

        if (input) {
            AddToHist(input);
            var msgdata = {'opcode':'message', 'msg':input, 'room':'global'};
            var args = {type:"POST", url:"m/", data:msgdata, complete:ReceiveMessage};
            $.ajax(args);
            $('#ShoutboxTextBox').val("");
        }
        return false;
    };


    /* Receive function for every kind of messages.*/
    var ReceiveMessage = function (res, status) {
        if (status == "success") {
            var obj = jQuery.parseJSON(res.responseText);

            if (!obj) {
                return false;
            }
            var i;
            for (i = 0; i < obj.count; ++i) {
                if (obj.msgs[i].room == 'global' && initial == 0) {
                    $('#ShoutboxTextArea').append(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />");
                    AutoScroll();
                }
                else {

                    if (!IsForMe(obj.msgs[i].room)) {
                    } else {
                        room = GetRoom(obj.msgs[i].room);
                        if (RoomNotExist(obj.msgs[i].room)) {

                            if (room >= 2) {
                                select_bar(room, obj.msgs[i].user);
                                room_id[room] = obj.msgs[i].room;
                                users_name[room] = obj.msgs[i].user;
                                text_context[room] = '';
                                log_number[room] = 0;


                            }
                            else {
                                if (max_room > room)
                                    $('#Privatebox' + room).show();
                                else
                                    init_chat(room);
                                insert_log_button(room);

                                $("#UserName" + room).attr('value', obj.msgs[i].user);
                                $("#UserNameMinimize" + room).attr('value', obj.msgs[i].user);
                                room_id[room] = obj.msgs[i].room;
                            }
                        }

                        if (room > 2) {
                            log_number[room]++;
                            text_context[room] += obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + " <br />";
                            SW(room);
                        }
                        else {
                            if (obj.msgs[i].user != myName && timer[room] == null) {
                                timer[room] = 1;
                                ti[room] = setInterval('SwitchColor(room)', 500);
                            }
                            //chat_room = obj.msgs[i].room;
                            log_number[room]++;
                            $('#PrivateboxTextArea' + room).append(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />");
                            $('#PrivateboxTextArea' + room).scrollTop($('#PrivateboxTextArea' + room)[0].scrollHeight);
                        }
                    }
                }
            }


        }
        /*For not spaming*/
        else if (res.status == 400) {
            $('#ShoutboxTextArea').append('<p id="warn_spam"> Stop spamming! </p>');
        }

    };


    $('#ShoutboxSendButton').click(SendMessage);

    /* History for keys.*/
    function HistUp() {
        if (was_writing) {
            /* bagat in hist */
            var input = $('#ShoutboxTextBox').val();
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
            $('#ShoutboxTextBox').val(hist[j]);
            j = (j + 9) % 10;
            k++;
            change_dir = 1;
        }
    }

    function HistDown() {
        if (k == 0 && !was_writing) {
            $('#ShoutboxTextBox').val("");
        }

        else if (change_dir) {
            change_dir = 0;
            //j = (j + 1) % 10;
            /*k--;*/
        }

        if (k) {
            j = (j + 1) % 10;
            $('#ShoutboxTextBox').val(hist[j]);
            k--;
        }
    }

    /* Global chat key events. */
    $("#ShoutboxTextBox").keyup(function (event) {
        if (event.keyCode == 13) {
            /* enter */
            $("#ShoutboxSendButton").click();
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


});




