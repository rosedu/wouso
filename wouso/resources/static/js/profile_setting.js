
function get_nickname(){
    return $("#Nick_Name").val();
}

function get_firstname(){
    return $("#First_Name").val();
}

function get_description(){
    return $("#Description").val()
}
var url_base = '';
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
                window.location = '/player/' + myID
            },
            error: function(data) {
                $("#ajax-message").html("<p class='wrong'>Nickname-ul exista!</p>")
            }};
        $.ajax(args);
    }else
        $("#ajax-message").html("<p class='wrong'>Nume sau nickname prea scurt.</p>")

}

