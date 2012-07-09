
var selectID= null;
var UserName = null;

function select(id, uid, Name){
    selectID = id
    myID = uid
    UserName = Name
}



$(document).ready(function() {


    /* clear on refresh */
    $('#ShoutboxTextArea').val("");
    $('#ShoutboxTextBox').val('');


    /* create an emtpy array sized for 10 elements */
    var hist = [];
    var i = hist.length % 10; // iter pentru inserare
    var j = (i + 9) % 10; // iter pentru de unde incepe cautarea
    var k = 0; // iter pentru pasi de history
    var nr_max_steps; // limita pt k
    var change_dir; // anti inertie la schimbare de directie
    var was_writing;
    var room_id = [];

    $("#Privatebox1").hide();
    $("#PrivateboxMinimize1").hide();

    $("#Privatebox2").hide();
    $("#PrivateboxMinimize2").hide();


    /* hide button */
    $("#ShoutboxHideButton").click(function() {
        $("#Shoutbox").hide("slide", {direction: "right"});
        $("#ShoutboxShowButton").delay("350").show("slide", {direction:"right"});
    });

    /* show button */
    $("#ShoutboxShowButton").click(function() {
        $("#ShoutboxShowButton").hide();
        $("#Shoutbox").show("slide", {direction: "right"});
    });

    /* profile button */
    $("#ShoutboxProfileButton").click(function() {
        if(selectID != null){
            var url_profile = "/player/"+ selectID + "/";
            window.location = url_profile
        }
    });

    /* write a messaje button */
    $("#ShoutboxMesajeButton").click(function() {
        if(selectID != null){
            var url_profile = "/m/create/to="+ selectID;
            window.location = url_profile
        }
    });



    /* private button events */
    $("#ExitButton1").click(function(){
        $("#PrivateboxTextArea1").text("")
        $("#Privatebox1").hide();
    })

    $("#ExitButtonMinimize1").click(function(){
        $("#PrivateboxTextArea1").text("")
        $("#PrivateboxMinimize1").hide();
    })

    $("#UserName1").click(function(){
        $("#Privatebox1").hide();
        $("#PrivateboxMinimize1").show();

    })

    $("#UserNameMinimize1").click(function(){
        $("#Privatebox1").show();
        $("#PrivateboxMinimize1").hide();

    })


    $("#ExitButton2").click(function(){
        $("#PrivateboxTextArea2").text("")
        $("#Privatebox2").hide();
    })

    $("#ExitButtonMinimize2").click(function(){
        $("#PrivateboxTextArea2").text("")
        $("#PrivateboxMinimize2").hide();
    })

    $("#UserName2").click(function(){
        $("#Privatebox2").hide();
        $("#PrivateboxMinimize2").show();

    })

    $("#UserNameMinimize2").click(function(){
        $("#Privatebox2").show();
        $("#PrivateboxMinimize2").hide();

    })



    var firstFreeChat = 1;

    var chat_room = "null=null"
    /* chat button*/
    $("#C").click(function() {
        if(selectID != null){

            if (selectID == myID)
                alert("Nu ai cum sa faci chat cu tine")
            else if (selectID < myID)
                chat_room = selectID + "-" + myID;
            else
                chat_room = myID + "-" + selectID;

            var print = '#ShoutboxUserList';
            $(print).append(chat_room + "</br>");

            if (selectID != myID){

                $('#Privatebox' + firstFreeChat).show();

                $("#UserName" + firstFreeChat).attr('value', UserName+'     _')
                $("#UserNameMinimize" + firstFreeChat).attr('value',UserName + '     _')
                room_id[firstFreeChat] = chat_room
                firstFreeChat ++;
            }
        }
    })


    /* csrf crap */
    $.ajaxSetup({
                beforeSend: function(xhr, settings) {
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

    function AutoScroll() {
        $('#ShoutboxTextArea').scrollTop($('#ShoutboxTextArea')[0].scrollHeight);
    }

    function SendPing() {
        var mdata = {'opcode': 'keepAlive'};
        var args = {type:'POST', url:'m/', data:mdata, complete:ReceiveMessage};
        $.ajax(args);
    }


    function NewUsers() {
        $.get('/chat/last/', function (data) {
			$('#ShoutboxUserList').html(data);
		});
    }

    function NewLog() {
        $.get('/chat/log/', function (data) {
			$('#ShoutboxTextArea').html(replace_emoticons(data));
            $(document).ready(AutoScroll);

        });

    }

    $(document).everyTime(500, AutoScroll);
    $(document).ready(NewUsers);
    $(document).everyTime(6000, NewUsers);
    $(document).ready(NewLog);
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

    function isForMe(room){
        var first = room.split("-")
        var i
        for (i = 0; i < first.length; i++)
            if(myID == first[i])
                return true

        return false

    }


    function getRoom(room){
        var i
        for (i = 1; i <= firstFreeChat; i++)
            if(room_id[i] == room)
                return i
        firstFreeChat ++
        return firstFreeChat - 1
    }

    var SendMessage1 = function(id) {
        var input = $('#PrivateboxTextBox' + id).val();

        if (input) {
            var msgdata = {'opcode':'message', 'msg':input, 'room': room_id[id]};
            var args = {type:"POST", url:"m/", data:msgdata, complete:ReceiveMessage};
            $.ajax(args);
            $('#PrivateboxTextBox' + id).val("");
        }
        return false;
    };

    var SendMessage = function() {
        var input = $('#ShoutboxTextBox').val();

            if (input) {
                AddToHist(input);
                var msgdata = {'opcode':'message', 'msg':input, 'room': 'global'};
                var args = {type:"POST", url:"m/", data:msgdata, complete:ReceiveMessage};
                $.ajax(args);
                $('#ShoutboxTextBox').val("");
        }
        return false;
    };



    var ReceiveMessage = function(res, status) {
        if (status == "success") {
            var obj = jQuery.parseJSON(res.responseText);

            if (!obj) {
                return false;
            }
            var i;
            for (i = 0; i < obj.count; ++i) {
                if(obj.msgs[i].room != 'global'){

                    if(isForMe(obj.msgs[i].room)){
                        room = getRoom(obj.msgs[i].room)
                        if($('#Privatebox' + room).is(':hidden') && $('#PrivateboxMinimize' + room).is(':hidden') ){
                            $('#Privatebox' + room).show()
                            $("#UserName" + room).attr('value',obj.msgs[i].user+'     _')
                            $("#UserNameMinimize" + room).attr('value',obj.msgs[i].user + '     _')
                            room_id[room] = obj.msgs[i].room
                        }
                        chat_room = obj.msgs[i].room
                        $('#PrivateboxTextArea'+room).append(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />" )

                    }
                }
                else if(obj.msgs[i].room == 'global')
                $('#ShoutboxTextArea').append(obj.msgs[i].user + " : " + replace_emoticons(obj.msgs[i].text) + "<br />" )
            }

        }
		/*For not spaming*/        
		else if (res.status == 400) {
            $('#ShoutboxTextArea').append('<p id="warn_spam"> Stop spamming! </p>');
        }
        AutoScroll();

    };




    $('#ShoutboxSendButton').click(SendMessage);

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


    $("#PrivateboxTextBox1").keyup(function(event) {
        if (event.keyCode == 13) {
            /* enter */
           SendMessage1(1)
        }
    });

    $("#PrivateboxTextBox2").keyup(function(event) {
        if (event.keyCode == 13) {
            /* enter */
            SendMessage1(2)
        }
    });

    $("#ShoutboxTextBox").keyup(function(event) {
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



    var emoticons = {
        '>:D' : 'emoticon_evilgrin.png',
        ':D' : 'emoticon_grin.png',
        '=D' : 'emoticon_happy.png',
        ':\\)' : 'emoticon_smile.png',
        ':O' : 'emoticon_surprised.png',
        ':P' : 'emoticon_tongue.png',
        ':\\(' : 'emoticon_unhappy.png',
        ':3' : 'emoticon_waii.png',
        ';\\)' : 'emoticon_wink.png',
        '\\(ball\\)' : 'sport_soccer.png'
    }

    var img_dir = "/static/img/";
    function replace_emoticons(text) {
        $.each(emoticons, function(char, img) {
            re = new RegExp(char,'g');
            text = text.replace(re, '<img src="'+img_dir+img+'" />');
        });

        return text;
    }



});




