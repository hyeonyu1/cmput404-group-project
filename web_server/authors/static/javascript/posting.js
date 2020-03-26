
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
	fetch("/author")
		.then(response => {
			return response.json()
		})
		.then(data => {
			let select = document.querySelector('#visibleFor');
			select.multiple = true;
			select.innerHTML = ''; // Clear out the current options
			for(let author of data.data){
				if(!author.uid) continue;
				//console.log("AUTHOR ID", author.uid, author)
				let opt = document.createElement('option');
				opt.value = author.uid;
				opt.innerText = (author.display_name || author.first_name + author.last_name || "NO NAME")
					+ " [" + author.uid.replace(/http[s]+:\/\//,'').slice(0, 10) + '...' + author.uid.slice(-5) + "]";
				if (selectedUsers != undefined) {
					if (selectedUsers.includes(author.uid)){
						opt.selected = 'selected';
					}
				}
				select.appendChild(opt)
			}
		})
}


