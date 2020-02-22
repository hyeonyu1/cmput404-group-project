var visibility = document.getElementById("visi");

var visibleTo = document.getElementById("checkPrivate");


function visibility_changed(){
	if (visibility.value == 'private') {
	    document.getElementById("visibleTo").style.visibility = "visible";
	}
	else {
		document.getElementById("visibleTo").style.visibility = "hidden";
	}
}
