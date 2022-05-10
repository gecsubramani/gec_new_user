
function loadHtml(id, filename){

	let xhttp;
	let element = document.getElementbyId(id);
	let file = filename;
	
	if (file ) {
		xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function(){
			if (this.readystate == 4){
				if (this.status == 200) {element.innerHTML = this.responseText;}
				if (this.status == 404) {element.innerHTML = "<h1>Page not found</h1>";}
			}
		}
	
	}
	xhttp.open("GET", `changedocs/${file}`, true);
	xhttp.send();
	return;


}