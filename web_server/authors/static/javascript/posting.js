var visibility = document.getElementById("Visibility");

var visibleTo = document.getElementById("checkPrivate");


function visibility_changed(){
	if (visibility.value == 'private') {
	    document.getElementById("visibleTo").disabled = false;
	}
	else {
		document.getElementById("visibleTo").disabled = true;
	}
}
