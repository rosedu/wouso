/** Convertor
*/
function seconds2time( seconds )
{
	seconds = seconds%3600;
	minute = Math.floor(seconds/60);
	secunde = seconds%60;
	if(minute<10) minute ='0'+minute;
	if(secunde<10) secunde = '0'+secunde;
	return minute+':'+secunde;
}
function update(timerid) {
    text = seconds2time(seconds);
    seconds = seconds - 1;
    $('#' + timerid).html(text);
    if(seconds >= 0) {
        if (seconds < 30)
            $('#' + timerid).addClass('wrong');
		setTimeout( "update('"+timerid+"')", 1000);
    }
    else
        $('#challenge_form').submit();
}