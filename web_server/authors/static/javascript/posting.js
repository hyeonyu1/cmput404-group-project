
//Check when changing visibility if its set to private show a list of users
function visibilityChanged(selectedUsers){
	var visibility = document.getElementById("visi");
	var visibleTo = document.getElementById("checkPrivate");
	if (visibility.value === 'PRIVATE') {
		get_all_users(selectedUsers);
	    document.getElementById("visibleTo").style.visibility = "visible";
	}
	else {
		document.getElementById("visibleTo").style.visibility = "hidden";
	}
}

/**
 * Gets all the users available on the local system and populates the user selector so that
 * you can pick users when making a private post
 */
function get_all_users(selectedUsers){
	fetch("/author/available/")
		.then(response => {
			return response.json()
		})
		.then(data => {
			let select = document.querySelector('#visibleFor');
			select.multiple = true;
			select.innerHTML = ''; // Clear out the current options
			for(let uid of data.data){
				let opt = document.createElement('option');
				opt.value = uid;
				opt.innerText = uid;
				if (selectedUsers != undefined) {
					if (selectedUsers.includes(uid)){
						opt.selected = 'selected';
					}
				}
				select.appendChild(opt)
			}
		})
}


