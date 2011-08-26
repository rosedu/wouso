/* global reference */
var active_tab = null;

$(document).ready(function() {

    //When page loads...
    $(".tab_content").hide(); //Hide all content
    $("ul.tabs li:first").addClass("active").show(); //Activate first tab
    $(".tab_content:first").show(); //Show first tab content

    //On Click Event
    $("ul.tabs li").click(function() {

        $("ul.tabs li").removeClass("active"); //Remove any "active" class
        $(this).addClass("active"); //Add "active" class to selected tab
        $(".tab_content").hide(); //Hide all tab content

        var activeTab = $(this).find("a").attr("href"); //Find the href attribute value to identify the active tab + content
        $(activeTab).fadeIn(); //Fade in the active ID content
        $(activeTab).trigger("custom");
        active_tab = activeTab;
        return true;
    });

});

function tabToURL(tab_name, url) {
    $("#" + tab_name).bind('custom',
                    function() {
                        $.ajax({
                            url: url,
                            success: function(data) {
                                $("#" + tab_name).html(data)
                            }
                        })
                    });
}
