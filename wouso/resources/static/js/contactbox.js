var t = null;
var selectID_over;
var UserName_over;


jQuery(document).ready(function(){
    $(document).mousemove(function(e){
        tempX = e.pageX-15;
        tempY = e.pageY-15;
    });
});

function show_contact_box(){
    $("#Contactbox").show();
}

function on_userlist_mouseover(name, score, avatar, level, id, x_position) {
    selectID_over = null;
    UserName_over = null;
    t = setTimeout(function(){
        on_userlist_select1(id, name);
        var position = 1100;
        if(x_position == 1) position = tempX;
        $("#Contactbox").css("top",tempY+"px").css("left",position + "px");
        $("#Contactbox").show();
        var html = "<b>" + name  + "</b></br></br>" +
            "<div style='text-align:right'>Points " + score + "</br>Level "  + level + "</div>";
        $("#ContactboxName").html(html);
        var el = "<img class='avatar' src=" + avatar + " style='width:60px; height:60px'/>";
        $('#ContactboxAvatar').html(el);}, 1500);
}

function on_userlist_mouseout() {
    $("#Contactbox").hide();
    clearTimeout(t);
}

function on_userlist_select1(id, Name) {
    selectID_over = id;
    UserName_over = Name;
    $('.contactaction').attr('disabled', false);

    if (id == myID) $('#GlobalboxChatButton').attr('disabled', true);
}