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

/**
 * Given some text, scans the text for any markdown links that appear in the form {hostname}/{path}/{rest of the path}
 * and then returns a list of links that will be of form {hostname}/{replaced_path}/{rest of path}
 * @param content
 */
function scan_for_image_edit_links(content, hostname, path, replaced_path){
	// Get all markdown links
	let links = content.matchAll(/!\[([^\]]*)]\(https?:\/\/([^)]*)\)/g);

	// Filter for the ones that are for our own server
	let own_server_links = {};
	for(let link of links){
		// There are some capturing groups defined in the above regex that are useful
		let link_name = link[1];
		let link_uri = link[2];

		let prefix = hostname + '/' + path + '/';

		if(link_uri.startsWith(prefix)){
			// This is a link we need to extract and return a replacement version for
			own_server_links[link_name] = link_uri.replace(path, replaced_path)
		}
	}
	return own_server_links
}


