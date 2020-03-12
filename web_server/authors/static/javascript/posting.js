var visibility = document.getElementById("visi");

var visibleTo = document.getElementById("checkPrivate");


function visibilityChanged(){
	if (visibility.value === 'PRIVATE') {
		get_all_users();
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
function get_all_users(){
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

				let opt = document.createElement('option');
				opt.value = author.uid;
				opt.innerText = (author.display_name || author.first_name + author.last_name || "NO NAME")
					+ " [" + author.uid.replace(/http[s]+:\/\//,'').slice(0, 10) + '...' + author.uid.slice(-5) + "]";
				select.appendChild(opt)
			}
		})
}

