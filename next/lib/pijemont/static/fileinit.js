var data = {'args':null,'targets':null};
var ready = false;

function file_read(form){
    var reader = new FileReader();
    var set_onload = function(f){
	reader.onload = function(e) {
	    console.log('done with',f);
	    data[f] = e.target.result;
	    ready = data['args'] != null && data['targets'] != null;
	    document.getElementById(f+'_status').innerHTML='Ready!';
	};
	console.log('set onload',f);
    };
    set_onload(form);
    document.getElementById(form+'_status').innerHTML='Loading...';
    reader.readAsDataURL(document.getElementById(form+'_file').files[0]);
}

function submit_form(){
    if(!ready){
	alert('Please select both an arguments and a targets file, or wait until the files are ready.');
	return;
    }
    
    console.log(data);
    var XHR = new XMLHttpRequest();
    XHR.addEventListener("load", function(event) {
	console.log("DID IT",event.target.responseText);
    });
    XHR.addEventListener("error", function(event) {
	console.log('Oops! Something went wrong.');
    });
    XHR.open("POST", target);
    XHR.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    XHR.send(JSON.stringify(data));
    return false;
}