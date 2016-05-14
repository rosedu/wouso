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

    $('#ajaxBusy').css({
    display:"",
    margin:"0px",
    paddingLeft:"0px",
    paddingRight:"0px",
    paddingTop:"0px",
    paddingBottom:"0px",
    position:"absolute",
    right:"3px",
    top:"3px",
    width:"auto"
  });

    var answer_count = 1;
    var max = $("#answers").data("max-answers");

    function answer_element_template(i){
        return "<div id=\"answer_" +  i + "\">" + 
                "<label for=\"id_answer_" + i + "\">Answer " + (i+1).toString() + ":</label>" + 
                "<textarea id=\"id_answer_" + i + "\" rows=\"10\" cols=\"40\" name=\"answer_" + i +
                "\"></textarea>" + "<br/>" + "<label for=\"id_correct_ " + i + "\">Correct?</label>" +
                "<input id=\"id_correct_" + i + "\" name=\"correct_" + i + "\" type=\"checkbox\">" + 
                "</input></div><br/>";
    }

    $("#add_button").click(function(){
        answer_count++;
        if (answer_count < max){
            $("#answers").append(answer_element_template(answer_count));           
            if(answer_count == max - 1){
                $("#add_button").hide();
                }
            }
        });


});

$(document).ready(function(){
    $('.ajaxify_content').bind('click', function(){
        var url = url_base + $(this).attr('href');
        $.ajax({
            url : url,
            type : "GET",
            beforeSend: function(data){
                $("#content").html('<div id="ajaxBusy" class="hidden"><p><img src="/static/img/ajax-loader.gif"></p></div>');
                $('#ajaxBusy').show(); 
            },
            complete: function(data){
                $("#ajaxBusy").hide();
            },
            success: function(data){
                $("div#content").html(data);
                $('title').text($('.section h2').text());
                $(".proposed_question").click(function(event){
                    console.log("ahaha");
                    $(this).find("ul").toggle();
                });
            },
            error: function(data) {
                document.location = url;
            }
        });

        return false;
    });
});
