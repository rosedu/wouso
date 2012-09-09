$(document).ready(days_until_now);
function days_until_now(){
    var oneDay = 24*60*60*1000; // hours*minutes*seconds*milliseconds
    var firstDate = new Date(2012,07,01);
    var secondDate = new Date();

    var diffDays = Math.round(Math.abs((firstDate.getTime() - secondDate.getTime())/(oneDay)));
    var i;
    for(i = 0; i <= diffDays; i++){
        $("#choose_day").append("<option>"+ firstDate.getDate()+ "-" + (firstDate.getMonth()+1) + "-" + firstDate.getFullYear() +"</option> ")
        firstDate.setTime(firstDate.getTime() + oneDay);
    }
}
$(function() {
    $( "#datepicker" ).datepicker();
    });
