var prefix = '/rest/v1/authenticate';

function get_salt (login, cb, err) {
    console.log('auth.get_salt');
    jQuery.getJSON(prefix+'/salt?login='+login, function (json) {
	console.log('salt :' + json);
	
	if (json.salt)
	    cb(json.salt);
	else if (err)
	    err({reason: 'no salt', json: json});
    }).error(function(error) {
	if (err)
	    err(error);
    });
}

function login(login, pwd, cb, err) {
    console.log('auth.login');
    get_salt(login, function (salt) {
	var bcrypt = new bCrypt();
	bcrypt.hashpw(pwd, salt, function (hash) { 
	    jQuery.getJSON(prefix+'?login='+login+'&hash='+hash, function (json) {
		console.log(json);
		cb(json);
	    }).error(function (error) {
		if (err)
		    err(error);
	    });
	});
    }, function (error) {
	if (err)
	    err({reason: 'failed fetching salt', error: error});
    });
}    
