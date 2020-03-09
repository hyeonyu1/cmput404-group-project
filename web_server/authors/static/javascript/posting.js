var visibility = document.getElementById("visi");

var visibleTo = document.getElementById("checkPrivate");


function visibilityChanged(){
	if (visibility.value == 'PRIVATE') {
	    document.getElementById("visibleTo").style.visibility = "visible";
	}
	else {
		document.getElementById("visibleTo").style.visibility = "hidden";
	}
}

