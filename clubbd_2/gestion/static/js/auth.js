var prefix = '/rest/v1/authenticate';

function get_salt (login, cb) {
    jQuery.getJSON(prefix+'/salt/'+login, function (json) {
	cb(json.salt || 'error');
    });
}

function login(login, pwd, cb) {
    get_salt(login, function (salt) {
	var bcrypt = new bCrypt();
	bcrypt.hashpw(pwd, salt, function (hash) { 
	    jQuery.getJSON(prefix+'?login='+login+'&hash='+hash, function (json) {
		cb(json);
	    });
	});
    });
}    
