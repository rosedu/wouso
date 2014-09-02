/* global reference */
var active_tab = '#rec';


$(document).ready(function() {

    //When page loads...
    $(".tab_content").hide(); //Hide all content
    $("ul.nav-tabs li:first").addClass("active").show(); //Activate first tab
    $(".tab_content:first").show(); //Show first tab content

    //On Click Event
    $("ul.nav-tabs li").click(switchtab);

    //Load with hash
    hash = document.location.hash;
    $(hash + '-click').trigger('click');
});

function switchtab() {
    $("ul.nav-tabs li").removeClass("active"); //Remove any "active" class
    $(this).addClass("active"); //Add "active" class to selected tab
    $(".tab_content").hide(); //Hide all tab content

    var activeTab = $(this).find("a").attr("href"); //Find the href attribute value to identify the active tab + content
    $(activeTab).fadeIn(); //Fade in the active ID content
    $(activeTab).trigger("custom");
    active_tab = activeTab;
    return false;
}



/**
 * Executes when the user wants to load
 * newer or older messages
 * */
function getMessages(e, pageNumber, url) {

    $.ajax({
        data: {'page':pageNumber},
        url: url,
        success: function(data) {
            $(active_tab).html(data)
        }
    });

    e.preventDefault();
}

function tabToURL(tab_name, url) {
    $("#" + tab_name).bind('custom',
        function() {
            $.ajax({
                data: {'page':1},
                url: url,
                success: function(data) {
                    $("#" + tab_name).html(data)
                }
            })
        });
}
