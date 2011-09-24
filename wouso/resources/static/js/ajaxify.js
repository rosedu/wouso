/* convert all links with class ajaxify in smth smarter */
$(document).ready(function (){
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
