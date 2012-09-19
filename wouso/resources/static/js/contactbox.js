var time_for_chat_appear = null;
var time_for_chat_hide = null
var selectID_over;
var UserName_over;


jQuery(document).ready(function(){
    $(document).mousemove(function(e){
        tempX = e.pageX-15;
        tempY = e.pageY-15;
    });
    $(".cplayer").mouseover(set_mouseover);
    $(".cplayer").mouseout(set_mouseout);
});

function set_mouseout(){
    rel_data = $(this).attr("rel");
    var text = rel_data.split(",");
    on_userlist_mouseout(text[6]);
}

function set_mouseover(){
    rel_data = $(this).attr("rel");
    var text = rel_data.split(",");
    on_userlist_mouseover(text[0], text[1], text[2], text[3], text[4], text[5], text[6]);
}

function show_contact_box(){
    clearTimeout(time_for_chat_hide);
    $("#Contactbox").show();
}

function getElementTopLeft(id) {
    var ele = document.getElementById(id);
    var top = 0;
    var left = 0;
    var right = 0;
    while(ele.tagName != "BODY") {
        top += ele.offsetTop;
        left += ele.offsetLeft;
        ele = ele.offsetParent;
    }
    return { top: top, left: left, right: right};
}


function on_userlist_mouseover(nickname, name, score, avatar, level, id, x_position) {
    selectID_over = null;
    UserName_over = null;
    var position;

    time_for_chat_appear = setTimeout(
        function(){
            make_buttons_changes(id, nickname);

            if (x_position == 1){
                if(tempX + 220 > window.innerWidth)
                    position = window.innerWidth - 220;
                else
                    position = tempX;
            }else {
                var TopLeft = getElementTopLeft("GlobalboxUserList");
                if(TopLeft.left + 360 > window.innerWidth)
                    position = window.innerWidth - 220;
                else
                    position = TopLeft.left + 140
            }

            if(tempY + 145 > window.innerHeight)
                tempY = window.innerHeight - 145;

            $("#Contactbox").css("top",tempY+"px").css("left",position + "px");
            $("#Contactbox").show();

            name = name.split(/-| /);
            var html;
            if (name.length == 1)
                html = "<b>" + name[0] + "</b></br></br>";
            else
                html = "<b>" + name[0] + "</b></br><b>" + name[1] + "</b>";

            html +="<div style='text-align:right'>Points " + score + "</br>Level "  + level + "</div>";
            $("#ContactboxName").html(html);

            var avatar_img = "<img class='avatar' src=" + avatar + " style='width:60px; height:60px'/>";
            $('#ContactboxAvatar').html(avatar_img);
        }, 1500);
}


function on_userlist_mouseout(x_position) {
    if(x_position == 0){
        time_for_chat_hide = setTimeout(function(){$("#Contactbox").hide()},500);
    }
    else
        time_for_chat_hide = setTimeout(function(){$("#Contactbox").hide();},0);
    clearTimeout(time_for_chat_appear);

}

function make_buttons_changes(id, Name) {
    selectID_over = id;
    UserName_over = Name;
    $('.contactaction').attr('disabled', false);

    if (id == myID) $('#ContactboxChatButton').attr('disabled', true);
}