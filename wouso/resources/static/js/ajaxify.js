/* convert all links with class ajaxify in smth smarter */
var url_base = '';

// reload header 
function reload_header() {
    $.ajax({
        url: url_base + '/ajax/do/header/',
        success: function(data) {
            $('#topbar').html(data);
        },
        error: function(data) {
            // pass 
        }
    })
}
/*
$(document).ready(function (){
    // button links 
    $('.ajaxify').bind('click', function () {
        url = url_base + this;
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
*/
$(document).ready(function(){
    $('.ajaxify_content').bind('click', function(){
        var url = url_base + $(this).attr('href');
        $.ajax({
            url : url,
            type : "GET",
            success: function(data){
                $("div#content").html(data);
                $('title').text($('.section h2').text());
            },
            error: function(data) {
                document.location = url;
            }
        });

        return false;
    });
});

