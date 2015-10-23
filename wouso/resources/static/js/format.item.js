/**
 * Format Item - Autocomplete functionality.
 */

//var url_base = '/';

function setAutocomplete(id) {
    $(document).ready(function() {
        $(id).autocomplete( url_base + "/instantsearch/",
            {   minChars:3,
                matchSubset:1,
                matchContains:1,
                cacheLength:10,
                formatItem:formatItem,
                onItemSelect:function (li) {
                    var player_id = getSelectedPlayer(li);
                    $(id + '_value').val(player_id);
                },
                selectOnly:1
            }
        );
    });
}

function formatItem( row ) {
    return row[0] + "<br />"+
        row[1] + "<br />" +
        row[2] + "<br />" +
        row[6]+" "+
        "<small><i>" + row[4] + " (" + row[5] + ") " +
        row[3] + " puncte</small></i>" + "<span class='hidden'>:" + row[8] + "</span>";
}
function getSelectedPlayer(li) {
    var text = li.innerHTML;
    var id = text.substr(text.lastIndexOf(":") + 1);
    id = id.substr(0, id.indexOf("<"));

    return id;
}

function selectItem(li) {
    id = getSelectedPlayer(li);
    document.location = url_base + '/player/' + id + '/';
}

function manageItem(li) {
    id = getSelectedPlayer(li);
    document.location = url_base + '/cpanel/players/manage_player/' + id + '/';
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
        url: url_base + '/searchone/?q=' + $('#to_input').val(),
        success: function(data) {
            var res = data.split("|");
            messagingUpdate(res[0], res[1]);
        },
        error: function(data) {
            $('#to_input').css("color", "red")
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
        url: url_base + '/m/view/' + id + '/',
        success: function(data) {
            container.html(data);
        },
        error: function(data) {
            console.log('eroare');
            console.log(JSON.stringify(data));
        }
    });
    return false;
}

function messagingReload() {
    $(active_tab).trigger('custom');
}
