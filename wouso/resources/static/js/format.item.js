function formatItem( row ) {
    var str = location.pathname;
    str = str.replace(row[5],"");
    str = str.replace(/[^\/]/g,"");
    str = str.replace(/\//g,"../");
    
    return row[0] + "<br /><img align=\"absmiddle\" src=\""+ 
        str+row[4]+"\" /> "+
        "<small><i>" + row[2] + " (" + row[3] + ") " +
        row[1] + " puncte</small></i>";
}
function selectItem(li) {
    $("#nume_user").focus();
}

