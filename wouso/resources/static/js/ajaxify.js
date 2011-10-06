/* convert all links with class ajaxify in smth smarter */
/* reload header */
function reload_header() {
    $.ajax({
        url: '/ajax/header/',
        success: function(data) {
            $('#topbar').html(data);
        },
        error: function(data) {
            /* pass */
        }
    })
}

/* reload activity */
function reload_activity() {
    $.ajax({
        url: '/ajax/activity/',
        success: function(data) {
            $('#wall').html(data);
        },
        error: function(data) {
            /* pass */
        }
    })
}


$(document).ready(function (){
    /* button links */
    $('.ajaxify').bind('click', function () {
        url = this;
        $.ajax({
            url: url + '?ajax=1',
            success: function(data) {
                $('#ajax-message').html(data);
                $('#ajax-message').show();
            },
            error: function(data) {
                document.location = url;
            }
        });
        return false;
    });
});
