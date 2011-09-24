function formatItem( row ) {
    return row[0] + "<br />"+ 
        row[4]+" "+
        "<small><i>" + row[2] + " (" + row[3] + ") " +
        row[1] + " puncte</small></i>" + "<span class='hidden'>:" + row[6] + "</span>";
}
function selectItem(li) {
    $("#nume_user").focus();
}

function selectItemMessaging(li) {
    var text = li.innerHTML;
    var name = text.substr(0, text.indexOf("<"));
    var id = text.substr(text.lastIndexOf(":") + 1);
    id = id.substr(0, id.indexOf("<"));

    messagingUpdate(name, id);
}

function messagingUpdate(name, id) {
    var html = "<span class='to_user'><input type='hidden' id='to' name='to' value='" + id +   "' />" + name + "<a href='#' class='to_reset' id='to_reset'>x</a></span>";

    $('#to_container').html(html);
    $('#to_input').hide();
    $('#to_reset').bind('click', messagingReset);
}

function messagingReset() {
    $('#to_container').html('');
    $('#to_input').show();
}

function messagingOut() {
    $.ajax({
        url: '/searchone/?q=' + $('#to_input').val(),
        success: function(data) {
            var res = data.split("|");
            messagingUpdate(res[0], res[1]);
        },
        error: function(data) {
            $('#to_input').focus();
        }
    });
}

function messagingSubmit() {
    if (!document.getElementById('to')) {
        messagingOut();
        return false;
    }
    return true;
}

function messagingView(id) {
    var container;
    if (active_tab)
        container = $(active_tab);
    else
        container = $('#message');

    $.ajax({
        url: '/m/view/' + id,
        success: function(data) {
            container.html(data);
        }
    });
    return false;
}

function messagingReload() {
    $(active_tab).trigger('custom');
}
