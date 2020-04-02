
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
				select.appendChild(opt);
			}
			get_visible_to_names(select);
		})
}

/**
 * For the given select element, will cycle through all of it's options and if the
 * inner text is a valid profile link, then it will replace the inner text with the users display name and host
 * @param select_element
 */
function get_visible_to_names(select_element){
	let options = select_element.querySelectorAll('option');
	for(let option of options){
		fetch('/author/profile/' + option.innerText)
			.then(response => response.json())
			.then(data => {
				option.innerText = data.displayName + ' (' + option.innerText + ')'
			})
	}
}


