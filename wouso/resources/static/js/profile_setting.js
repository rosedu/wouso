var url_base = '';

function get_nickname(){
    return $("#Nick_Name").val();
}

function get_firstname(){
    return $("#First_Name").val();
}

function get_description(){
    return $("#Description").val()
}


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

function save_changes(){

    var msgdata = null;
    if(get_nickname().length > 2 && get_firstname().length > 2)
        msgdata = {'nickname':get_nickname, 'firstname':get_firstname, 'description':get_description};
    if (msgdata != null){
        var args = {
            type:"POST",
            url:url_base + "/player/set/s/",
            data:msgdata,
            success: function(data) {
                window.location = url_base + '/player/' + myID
            },
            error: function(data) {
                $("#ajax-message").html("<p class='wrong'>Nickname-ul exista!</p>")
            }};
        $.ajax(args);
    }else
        $("#ajax-message").html("<p class='wrong'>Nume sau nickname prea scurt.</p>")

}

