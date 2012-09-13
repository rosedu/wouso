
function get_nickname(){
    return $("#Nick_Name").val();
}

function get_firstname(){
    return $("#First_Name").val();
}

function save_changes(){
    var msgdata = {'nickname':get_nickname, 'firstname':get_firstname};
    var args = {
        type:"POST",
        url:"/player/set/s/",
        data:msgdata,
        success: function(data) {
            window.location = '/player/' + myID
        },
        error: function(data) {
            alert("eeerror")
        }};
    $.ajax(args);

}

